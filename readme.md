# Starbucks Offer Recommendation Project

## Project Description
The main goal of the project was to build a recommendation model that can provide customers to an appropriate offer. 
![intro](/images/intro.png)

The dataset contains simulated data that mimics customer behavior on the Starbucks rewards mobile app. Once every few days, Starbucks sends out an offer to users of the mobile app. An offer can be merely an advertisement for a drink (informational offer) or an actual offer such as a discount or BOGO (buy one get one free). 

Since not all users receive the same offer and not all users response to the offers in the same way, this is the challenge to solve with this data set. 

To build a recommendation model, we computed purchasing behavior scores (PB scores). Since every offer has a validity period, not all users buy products before the offer expires. Given PB scores, we can see the purchasing path from receiving offers to purchasing products. We computed PB scores with the following formula:

$$PB_{viewed} = \frac{10 * (\text{n_received}+(3 * \text{n_viewed}) + (5 * \text{n_completed}))}{9 * \text{n_received}}$$


For some cases where customers did not view the offer but completed to buy products, we have different formula to compute PB scores:

$$PB_{NOTviewed} = \frac{10 * (\text{n_received} + (8 * \text{n_viewed})}{9 * \text{n_received}}$$


Based on PB scores, we made customers-offers pair matrix which has a lot of NaN values, so we used FunkSVD algorithm to build the recommendation model. 

We tried different parameters by changing learning_rate, latent_features and iteration. 

The model with learning_rate = 0.0008 looked promising, so the final model's parameter was learning_rate=0.0008, latent_features=10, and iteration=150. 


## Visualization












## Licence
This project is the part of Data Science Nanodegree Program by Udacity. Data were provided by Udacity.