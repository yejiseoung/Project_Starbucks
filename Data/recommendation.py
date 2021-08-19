import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
import math
from sqlalchemy import create_engine

class Recommender():


    def __init__(self):
        """ don't need to make required attributes"""

    
    def load_data(self, df_score_pth, df_pth):
        self.df_score = pd.read_csv(df_score_pth)
        df_engine = create_engine('sqlite:///{}'.format(df_pth))
        self.df = pd.read_sql("SELECT * FROM starbucks", df_engine)

        return self.df_score


    def split_train_test(self, df_score):
        """ Function to create train and test dataset"""
        df_score = df_score.reset_index()

        total_size = df_score.shape[0]

        # 90% of the dataset for training data
        training_idx = np.random.choice(total_size, int(np.round(total_size * 0.9)), replace=False)
        testing_idx = np.setdiff1d(np.arange(0, total_size), training_idx)

        print('training_size:', len(training_idx))
        print('testing_size:', len(testing_idx))

        df_score_train = df_score.loc[training_idx].groupby(['customer_id', 'offer_number']).max() 
        df_score_test = df_score.loc[testing_idx].groupby(['customer_id', 'offer_number']).max()

        return df_score_train, df_score_test

    
    def fit(self, latent_features=10, learning_rate=0.0001, iters=250):

        self.df_score_train, self.df_score_test = Recommender.split_train_test(self, self.df_score)
        print(self.df_score_train.head(10))


        self.df_recs = self.df_score_train.groupby(['customer_id', 'offer_number'])['PB'].sum().unstack()
        
        print('df_recs:\n',self.df_recs.head(10))


        # Store more inputs
        self.latent_features = latent_features
        self.learning_rate = learning_rate
        self.iters = iters

        # set up useful values
        self.matrix = self.df_recs.values
        self.n_customers = self.matrix.shape[0]
        self.n_offers = self.matrix.shape[1]

        print('matrix shape:', self.matrix.shape)

        print(self.n_customers)
        print(self.n_offers)

        # if we have missing values, n_PB = n_customers * n_offers won't work
        self.n_PB = np.count_nonzero(~np.isnan(self.matrix))
        print(self.n_PB)

        # initialize the customers and offer matrices with random values
        customers_mat = np.random.rand(self.n_customers, self.latent_features)
        offer_mat = np.random.rand(self.latent_features, self.n_offers)

        plt_iteration = []
        plt_sse = []

        # initialize sse at 0 for first iteration
        sse_accum = 0

        # Keep track of iteration and MSE
        print("Optimization Statistics")
        print("Iterations | Mean Squared Error")


        # for each iteration
        for iteration in range(self.iters):

            # update our sse
            old_sse = sse_accum
            sse_accum = 0

            # for each customers-offer pair
            for customer in range(self.n_customers):
                for offer in range(self.n_offers):

                    # if the PB score exists (not None)
                    if not np.isnan(self.matrix[customer, offer]):

                        # compute the error as the actual minus the dot product
                        # of the customers and offer latent features
                        diff = self.matrix[customer, offer] - np.dot(customers_mat[customer, :], offer_mat[:, offer])

                        # keep track of the sum of squared errors for the matrix
                        sse_accum += diff**2

                        # update the values in each matrix in the direction of the gradient
                        for k in range(self.latent_features):
                            customers_mat[customer, k] += self.learning_rate * (2 * diff * offer_mat[k, offer])
                            offer_mat[k, offer] += self.learning_rate * (2 * diff * customers_mat[customer, k])

            # print results
            print("%d \t\t %f" % (iteration+1, sse_accum / self.n_PB))


            # if iteration % 10 == 0:
            plt_iteration.append(iteration)
            plt_sse.append(np.round(sse_accum / self.n_PB, 2))

        
        
        plt.plot(plt_iteration, plt_sse)
        plt.grid(linestyle='--')
        plt.xlabel('Iteraton')
        plt.ylabel('Mean Squared Error (MSE)')
        plt.title('MSE vs. Iteration')
        plt.show()

        # keep customers_mat and offer_mat
        self.customers_mat = customers_mat
        self.offer_mat = offer_mat


    def make_comparison(self, customer_id):
        self.preds_mat = np.dot(self.customers_mat, self.offer_mat)
        print(self.df_recs.loc[customer_id].values)
        print(np.round(self.preds_mat[customer_id], 2))


    def recommend(self, customer_id, average_score=5.67):
        lst_to_recommend=[]
        #self.preds_mat = np.dot(self.customers_mat, self.offer_mat)

        for i, score in enumerate(self.preds_mat[customer_id]):
            if score > average_score:
                lst_to_recommend.append("offer_" + str(i))

        return lst_to_recommend

        



if __name__ == '__main__':
    import recommendation as r

    # instantiate recommender
    rec = r.Recommender()

    # load data
    rec.load_data(df_score_pth='../Data_ing/df_score.csv', df_pth='../Data_ing/starbucks.db')

    # fit recommender 
    rec.fit(latent_features=10, learning_rate=0.0008, iters=100)
    
    # make comparison
    rec.make_comparison(customer_id=945)

    # print
    print('recommend the following offers for customers:', rec.recommend(945, 5.67))

    #rec.make_comparison(customer_id=1)
    #print('recommend the following offers for customers:', rec.recommend(1, 5.67))
    




