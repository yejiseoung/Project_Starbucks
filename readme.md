# Starbucks Offer Recommendation Project

## Project Description

![intro](/images/intro.png)


The main goal of the project was to build a recommendation model that can provide customers to an appropriate offer. 

The dataset contains simulated data that mimics customer behavior on the Starbucks rewards mobile app. Once every few days, Starbucks sends out an offer to users of the mobile app. An offer can be merely an advertisement for a drink (informational offer) or an actual offer such as a discount or BOGO (buy one get one free). 

Since not all users receive the same offer and not all users response to the offers in the same way, this is the challenge to solve with this data set. 

To build a recommendation model, we computed purchasing behavior scores (PB scores). Since every offer has a validity period, not all users buy products before the offer expires. Given PB scores, we can see the purchasing path from receiving offers to purchasing products. We computed PB scores with the following formula:


![PB_score_viewd](/images/PB_viewed.png)

For some cases where customers did not view the offer but completed to buy products, we have different formula to compute PB scores:

![PB_score_not_viewed](/images/PB_notviewed.png)


Based on PB scores, we made customers-offers pair matrix which has a lot of NaN values, so we used FunkSVD algorithm to build the recommendation model. 

We tried different parameters by changing learning_rate, latent_features and iteration. 

![learning_rate_graph](/images/learning_rate.png)

The model with learning_rate = 0.0008 looked promising, so the final model's parameter was learning_rate=0.0008, latent_features=10, and iteration=100. 

![last_model](/images/last_model.png)


Finally, the model recommends offer numbers based on customer_id. For example, the model recommended offers for customer_id = 945. 

![recommend](/images/recommend.png)


## Executing Program:
1. Run the following commends in terminal to clean data and store the cleaned data

`python Data/process_data.py Data/portfolio.json Data/profile.json Data/transcript.json Data/starbucks.db`


2. Run the following commends to create df_score.csv

`python Data/create_df_score.py Data/portfolio.json Data/profile.json Data/transcript.json Data/df_score.csv`

3. Run `python Data/recommendation.py`
In recommendation.py, you can change parameters for the model and put specific customer id to see the offer recommendation. 


## File Descriptions
The files structure is arranged as below:

    - Data
        - process_data.py - clean portfolio, profile, and transcript json files and combine them
        - create_df_score.py - create df_score csv file which has customer_id, offer_numbers and PB score
        - recommendation.py - create df_recs matrix which has customers-offers pairs. df_recs is sparse matrix, so we created FunkSVD algorithm to build the recommendation model. Also, it performs model evaludation by creating mean-squared-error plot based on model iterations. 
        - portfolio.json - a dataset
        - profile.json - a dataset
        - transcript.json - a dataset

    - Starbucks.ipynb shows the entire workflow including cleaning data, visualizing data, building the model, and evaludating model. 
    - readme.md



## Visualization
We created graphs to see the patterns or distributions in dataset. Here are some examples:

![graph1](/images/d_offer_types.png)

Customers have gotten BOGO or discount offers more than informational offers.


![graph2](/images/d_offer_numbers.png)




## Licence
This project is the part of Data Science Nanodegree Program by Udacity. Data were provided by Udacity.