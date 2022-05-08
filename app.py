from web3 import Web3, HTTPProvider
from web3.beacon import Beacon
import json
import requests
import pandas as pd
import itertools
import threading
import time
import sys

#Setting up output for pandas
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

#Connecting to the beacon chain infura API using web3.py
w3 = Beacon('https://28pLaytcNJFemy0X4pomhog4WBP:8b03393b0223b1cd84b56d2d377e931a@eth2-beacon-prater.infura.io')



#Function to animate while the transactions are being fetched
done = False
def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rFetching Validators From The Beacon Chain ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!                                                   ')


#query to fetch parameters for the various knots in the the various stakehouses
query= """query{
    knots {
    id
    knotIndex
    isolatedDETH
    totalDETHRewardsReceived
    kicked
    historicallySlashed
    currentSlashedAmount
		stakeHouseMetadata{
      totalAmountOfSlotSlashed
      sETHRedemptionRateFormatted
      sETHExchangeRateFormatted
      sETHPayoffRateFormatted
      dETHMintedWithinHouse
      id
    }
    }
  }"""

#Fetching the api
url = 'https://api.thegraph.com/subgraphs/name/bswap-eng/stakehouse-protocol'
r = requests.post(url, json={'query': query})
json_data = json.loads(r.text)

#saving the details of the validators as pandas dataframe
df_data = json_data['data']['knots']
df = pd.DataFrame(df_data)

#creating different columns for stakehouse features of the validators.
df2=  pd.json_normalize(df.stakeHouseMetadata)
df2= df2.rename(columns={'id': 'stakehouse'})
df = pd.concat([df, df2], axis=1)
df.drop("stakeHouseMetadata", axis=1, inplace=True)
#Formatting the features to ETH
df['isolatedDETH'] = df['isolatedDETH'].apply(lambda x: int(x)/(10**18))
df['totalDETHRewardsReceived'] = df['totalDETHRewardsReceived'].apply(lambda x: int(x)/(10**18))
df['dETHMintedWithinHouse'] = df['dETHMintedWithinHouse'].apply(lambda x: int(x)/(10**18))
df['historicallySlashed'] = df['historicallySlashed'].apply(lambda x: int(x)/(10**18))
df['currentSlashedAmount'] = df['currentSlashedAmount'].apply(lambda x: int(x)/(10**18))
df['totalAmountOfSlotSlashed'] = df['totalAmountOfSlotSlashed'].apply(lambda x: int(x)/(10**18))


#fetching validdator features using the beacon chain API
t = threading.Thread(target=animate)
t.start()
eth= w3.get_validators(state_id= 'finalized')
time.sleep(10)
done = True

#creating dataframe for the beacon chain api
json_data = json.loads(json.dumps(eth))
eth_df= pd.DataFrame(json_data['data'])
eth_df2=  pd.json_normalize(eth_df.validator)
eth_df = pd.concat([eth_df, eth_df2], axis=1)
eth_df.drop(["validator","withdrawal_credentials"], axis=1, inplace=True)
eth_df['id']= eth_df['pubkey']

#combining the features from stakehouse api and the beacon chain api
df= df.join(eth_df.set_index(['id']), on= ['id'])
df.drop(["pubkey","activation_eligibility_epoch", "withdrawable_epoch"], axis=1, inplace=True)

#calculating cost based on the various parameters
df['cost']= df.apply(lambda row: (float(row['isolatedDETH'])- float(row['totalDETHRewardsReceived'])+ (100*float(row['kicked']))+ (100*float(row["slashed"])) + (1000*float(row["historicallySlashed"])) + (1000*float(row["currentSlashedAmount"]))+ (1000*float(row["totalAmountOfSlotSlashed"])) - (100* float(row["sETHRedemptionRateFormatted"])) - (100* float(row["sETHPayoffRateFormatted"])) - (100* float(row["effective_balance"])/(10**18)) - (100* float(row["balance"])/(10**18))  ), axis=1  )

df= df.sort_values(by= 'cost', ascending= True)

#best validators registered with stakehouse
print("\n Best knots are-\n")
df= df.reset_index()
print(df['id'], '\n')


df_stakehouse= df.groupby(['stakehouse']).sum()
df_stakehouse= df_stakehouse.sort_values(by= 'cost', ascending= True)
df_stakehouse= df_stakehouse.reset_index()
print("Best stakehouses are-")
print(df_stakehouse['stakehouse'])


