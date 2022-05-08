# Stakehouse
----
This project is dedicated towards getting the best out of the amazing *[Stakehouse](www.joinstakehouse.com)* protocol which aims at revolutionizing how POS staking works in ETH2.

This project uses the following two APIs to get features of the various knots of the stakehouse platform-

* [Stakehouse GraphQL API](https://thegraph.com/hosted-service/subgraph/bswap-eng/stakehouse-protocol)
* [Ethereum Beacon Chain API](https://ethereum.github.io/beacon-APIs/#/)

----


### Running the application
To install the dependencies simply run-
```
pip install -r requirements.txt
```

To get the best validators run-
```
python app.py
```
<br>
<div align="center" class="row">
  <img src="https://i.imgur.com/9I1Xi5k.gif" width="400"/>
</div>
<br>

----

### Getting the best validators

If we consider all the fields associated with a validator to be some cost associated with it, our problem of selecting the best knots can be modelled as a optimization problem where our aim is to minimize total cost.

For the fields like *slashed* and *kicked* which are represented as boolean, they are converted to integer and then added to the cost for the sake of minimisation.


The total cost can be calculated using the function-


![equation](https://latex.codecogs.com/svg.image?\begin{equation}&space;&space;&space;&space;C_p(\overline{y})=&space;\sum_{d&space;\in&space;D}y_d\&space;&space;F_{d}\&space;\forall\&space;d&space;\in&space;D\end{equation})

Here total cost ![equation](https://latex.codecogs.com/svg.image?C_p) is just the summation of all the costs ![equation](https://latex.codecogs.com/svg.image?y_d) multiplied by a constant ![equation](https://latex.codecogs.com/svg.image?F_d) that is used to convert all the costs to same unit. We perform the summation over all the fields of validator that helps in computing the performance.

The costs considered for selecting the best validators are-

* ![equation](https://latex.codecogs.com/svg.image?E_y) = Total dETH Rewards recieved by the validator
* ![equation](https://latex.codecogs.com/svg.image?H_{y})= Total amount historically slashed for the validator
* ![equation](https://latex.codecogs.com/svg.image?T_y)= Total amount of slashed for a validator
* ![equation](https://latex.codecogs.com/svg.image?R_y)= The sETH redemption rate for the house to which the validator belongs
* ![equation](https://latex.codecogs.com/svg.image?P_y)= The sETH payoff rate for the house to which the validator belongs.
* ![equation](https://latex.codecogs.com/svg.image?B_y)= Balance of the validator on the beacon chain
* ![equation](https://latex.codecogs.com/svg.image?EB_y)= Effective balance over which rewards are calculated for the validator on the beacon chain.
* ![equation](https://latex.codecogs.com/svg.image?K_y)= Whether the validator was kicked.
* ![equation](https://latex.codecogs.com/svg.image?S_y)= Whether the validator was slashed.

*Note- Here ![equation](https://latex.codecogs.com/svg.image?K_y) and ![equation](https://latex.codecogs.com/svg.image?S_y) are represented as deterministic value of either 1 or 0 and they are added to the complete cost equation by multiplying with a constant to increae their share of vote in total cost.*

Now for some fields like ![equation](https://latex.codecogs.com/svg.image?E_y) we want to maximise it instead of minimising. Hence while adding these fields, we add the negation of them such that the final cost equation becomes-

![equation](https://latex.codecogs.com/svg.image?C_p(\overline{y})=&space;(-E_y)&space;&plus;&space;H_y&plus;T_y&plus;&space;(-R_y)&plus;&space;(-P_y)&space;&plus;&space;B_y&space;&plus;&space;EB_y&space;&plus;&space;K_y&space;&plus;&space;S_y)

The aim here is to minimise the cost function ![equation](https://latex.codecogs.com/svg.image?C_p(\overline{y})) so as to get the best knots in the stakehouses.

The best stakehouses are determined by taking summation of the cost of all the validators associated with the stakehouse and minimising the cost.

### Output

The output is in form of a list of addresses which are the addresses of the validators from the best validator to the worst validators registered with the stakehouse.
Then best stakehouses are shown as a list of addresses indescending order of preference


