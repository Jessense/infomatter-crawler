import scipy.sparse as sp
from scipy import stats
import numpy as np
import mysql.connector
from config import *
import pickle


conn = mysql.connector.connect(
    user='root', password=sql_password, database='test')
conn.autocommit = True

START_WEIGHT = 2
BATCH_SIZE = 10

item_dict_del = dict()


def save_obj(obj, name, protocol):
    with open('obj/' + name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, protocol)


def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def get_rating():
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(id) FROM entries')
    entry_num = cursor.fetchone()[0]
    cursor.execute('SELECT MAX(id) FROM users')
    user_num = cursor.fetchone()[0]
    rating = np.zeros((user_num, entry_num), dtype=int)
    cursor.execute('SELECT * from readed')

    readed = cursor.fetchall()
    for item in readed:
        if item[1] and item[2]:
            rating[item[1]][item[2]] = +1

    cursor.execute('SELECT * FROM stars')
    stars = cursor.fetchall()
    for item in stars:
        if item[1] and item[2]:
            rating[item[1]][item[2]] += START_WEIGHT

    rating = sp.csr_matrix(rating)

    # 去0列
    num_item = rating.shape[1]
    item_dict = {i:i for i in range(num_item)}
    for i in range(num_item):
        temp_col = rating.getcol(i).toarray()
        if np.all(temp_col==0):
            item_dict.pop(i)

    i = 0

    rating2 = sp.lil_matrix(np.zeros([rating.shape[0], len(item_dict)]))
    for item_num in item_dict.values():
        item_dict_del[i] = item_num
        rating2[:,i] = rating.getcol(item_num)
        i += 1

    print(rating2.shape)
    rating2 = rating2.tocsr()

    save_obj(rating2, 'rating2', 3)
    # recommends = collaborative_filtering(sp.csr_matrix(rating2), BATCH_SIZE)
    # print(recommends)
    # for i in range(len(recommends)):
    #     for j in range(len(recommends[i])):
    #         add_recommend = ("INSERT INTO recommends "
    #                         "(user_id, entry_id) "
    #                         "VALUES (%s, %s)")
    #         cursor.execute(add_recommend, (i, recommends[i][j]))
    cursor.close()
    conn.close()


def collaborative_filtering(rating, topn):
    """
    :param rating_init: user-item matrix
    :param topn: top-n-rating items for user
    :return: predict rating matrix
    """

    similarity = sp.csr_matrix(np.zeros([rating.shape[1], rating.shape[1]]))
    ave_rating = dict()
    temparray = np.arange(rating.shape[0]).reshape(1,rating.shape[0])
    temparray_item = np.arange(rating.shape[1]).reshape((1,rating.shape[1]))
    sim_ifcount = sp.csr_matrix(np.zeros([rating.shape[1], rating.shape[1]]))
    len_i = rating.shape[1]
    rating = rating.toarray()
    for i in range(len_i):
        if i not in ave_rating:
            ave_rating[i] = np.average(rating[:,i])
        for j in range(rating.shape[1]):
            if sim_ifcount[i, j] == 1 or i == j:
                continue
            if j not in ave_rating:
                ave_rating[j] = np.average(rating[:, j])
            idx_i = rating[:,i] > 0
            idx_j = rating[:,j] > 0
            idx_i = temparray[0,idx_i]
            idx_j = temparray[0,idx_j]
            idx = np.intersect1d(idx_i, idx_j)
            rating_i = rating[idx, i]
            rating_j = rating[idx, j]
            rating_mean_i = np.mean(rating_i)
            rating_mean_j = np.mean(rating_j)
            sub_i = rating_i - rating_mean_i
            sub_j = rating_j - rating_mean_j
            dinominator = (np.sqrt(np.dot(sub_i, sub_i))*np.sqrt(np.dot(sub_j, sub_j)))

            if dinominator == 0:
                dinominator = 1
            similarity[j,i] = np.dot(sub_i,sub_j) / dinominator
            similarity[i,j] = similarity[j,i]

            sim_ifcount[j, i] = sim_ifcount[i, j] = 1

    predict = np.zeros([rating.shape[0],rating.shape[1]])
    predict_nlarge = np.zeros(rating.shape)

    # print('-------------')
    for u in range(predict.shape[0]):
        # predict
        idx_p = rating[u, :] == 0
        idx_p = temparray_item[0, idx_p]
        # train
        idx_t = rating[u, :] > 0
        idx_t = temparray_item[0, idx_t]
        for i in idx_p:
            sim = similarity[i, idx_t]
            rating_t = rating[u, idx_t]
            sim_sum = np.sum(sim)
            if sim_sum == 0:
                sim_sum = 1
            print(sim.toarray())
            print(rating_t)
            predict[u][i] = np.dot(sim.toarray(), rating_t) / sim_sum
        sort_index = np.argsort(-predict[u])
        sort_index = sort_index.tolist()[0:topn]
        predict_nlarge[u, sort_index] = predict[u, sort_index]

    return predict_nlarge, item_dict_del

#
# print(collaborative_filtering([],3))
rating3 = load_obj('rating2')
recommends = collaborative_filtering(rating3, BATCH_SIZE)
print(recommends)
