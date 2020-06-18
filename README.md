# Movie Recommender

The project is written in Python 3. Check *requirements.txt*.

Datasets integrated in the database:

* [Netflix](https://www.kaggle.com/Netflix-inc/Netflix-prize-data)
* [TMDB](https://www.kaggle.com/tmdb/tmdb-movie-metadata)

## Proof of concept

We first preprocess the data with the *preproc.py* and load the data indicating it by the first option when running *main.py*

Once the data is loaded, this is a possible subgraph of the database:

![alt text](https://github.com/tonibofarull/MovieRecommender/blob/master/images/subgraph.png)

Once the graph is loaded, in the following runs we can indicate that the data should not be reloaded.

The next options we have are:

* Id of the user requesting a recommendation.
* Number of recommendations requested.
* If you wish to filter by any genre.

Additionally, the system shows the scores of the user.

![alt text](https://github.com/tonibofarull/MovieRecommender/blob/master/images/out1.png)

And finally, the system returns a list of at most as many recommendations as the user has indicated.

![alt text](https://github.com/tonibofarull/MovieRecommender/blob/master/images/out2.png)

In addition, the user can choose to filter by selecting multiple genres, the system will display the list of possibilities. At the very least, the film has to be from one of the list. The selection of the genres is made using a list of the indexes. In case we show below are "Action" and "War".

![alt text](https://github.com/tonibofarull/MovieRecommender/blob/master/images/out3.png)

As we can see, in this case the system can show only 2 recommendations. As we have selected a genre from one of the films shown above, it is also shown here. Also, a movie is shown that had not been in the top before but in this case it does because of the filtering.

![alt text](https://github.com/tonibofarull/MovieRecommender/blob/master/images/out4.png)
