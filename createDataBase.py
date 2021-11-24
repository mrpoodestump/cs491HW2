import tweepy
import yaml
import networkx as nx
import matplotlib.pyplot as plt
import sqlite3
import json
import os
import matplotlib.pyplot as plt
import scipy as sp
from pyvis.network import Network
import numpy as np
from math import isclose
net = Network(notebook=True)



# yaml file reader funtion
def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

# yaml config file path
file_path = "twitter_api_key_config.yaml"


# read from config file
api_credential = read_yaml(file_path)

# API authentication
auth = tweepy.OAuthHandler(api_credential["api_key"],
                           api_credential["api_secret_token"])
auth.set_access_token(api_credential["access_token"],
                      api_credential["access_token_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True)

con = sqlite3.connect('KevinsNetwork.db')
cur = con.cursor()

try:
    cur.execute('''CREATE TABLE users (user_id BIGINT, username)''')
    cur.execute('''CREATE TABLE followers (user_id, follower_id)''')
    print('succesfully created DATABASE!!!')
except Exception:
    print("database already exists, moving on: ", Exception)

con.commit()


def test_database(kevin_id):
    con = sqlite3.connect('KevinsNetwork.db')
    cur = con.cursor()

    data = cur.execute(f"SELECT * FROM followers WHERE user_id={kevin_id}")
    for thing1, thing2 in data:
        print("thing1: ", thing1, "thing2: ", thing2)


def seed_user_followers(seed_user_id):
    cur.execute(f"SELECT * FROM users WHERE user_id='{seed_user_id}'")
    single = cur.fetchone();
    if single:
        for thing in single:
            print("thing? ", thing, " ? ")
        print('username already in database')
        return
    try:
        user_object = api.get_user(user_id=seed_user_id)
        user_id = user_object.id
        user_screen_name = user_object.screen_name
    except:
        print('user not reachable by tweepy')
        return

    ids = []
    cur.execute("INSERT INTO users VALUES(?, ?)", (user_id, user_screen_name))
    try:
        for followers in api.get_follower_ids(user_id=seed_user_id, cursor=-1):
            ids.extend(followers)
    except:
        print('followers not accessible, returning')
        return

    for followerID in ids:
        if followerID != 0 or followerID != '0':
            cur.execute('''INSERT INTO followers VALUES(?, ?)''', (user_id, followerID))

    data = cur.execute(f"SELECT * FROM followers WHERE user_id={user_id}")
    for thing1, thing2 in data:
        print("userID: ", thing1, "followerID: ", thing2)

    con.commit()


def get_random_follower(user_id):
    data = cur.execute(f"SELECT follower_id FROM followers WHERE user_id={user_id} ORDER BY RANDOM() LIMIT 1")
    for thing in data:
        print('What is random follower yoyoyoy :', thing)
        return thing


def count_rows():
    row_count = cur.execute("SELECT COUNT(*) FROM users")
    for thing in row_count:
        print('thing0', thing[0])
        return thing[0]

def new_users_row_count():
    row_count = cur.execute("SELECT COUNT(*) FROM new_users")
    for thing in row_count:
        print('new users row count', thing[0])
        return thing[0]


def loop_and_grow():
    count = 1
    seed_follower_id = 132321192
    while count_rows() <= 500:
        seed_user_followers(seed_follower_id)
        random_follower_id = get_random_follower(seed_follower_id)
        print('random follower ', random_follower_id)
        try:
            random_follower_object = api.get_user(user_id=random_follower_id[0])
        except:
            print("couldn't get random follower must move on")
            random_follower_id = get_random_follower(132321192)
            seed_follower_id = random_follower_id[0]
            continue
        print(random_follower_object.screen_name)
        seed_follower_id = random_follower_id[0]
        print('seed follower id', seed_follower_id)
        count = count + 1
        print('count: ', count)


def add_nodes_to_graph():
    G = nx.DiGraph()
    users = cur.execute(f"SELECT * FROM users").fetchall()

    count = 0
    for user_id, user_name in users:
        if count == 2:
            break
        followers_of_user = cur.execute(f"SELECT * FROM followers WHERE user_id={user_id}").fetchall()
        # print('followers of user', followers_of_user)
        # print('user_id: ', user_id,' user_name: ', user_name)
        for userId, follower in followers_of_user:
            print("follower: ", follower)
            G.add_edge(follower, user_id)
        count = count + 1

    # net.from_nx(G)
    # net.show('social graph')
    nx.readwrite.write_edgelist(G, 'hamGraph.csv')


def is_in_database(random_follower_id):
    is_in_database_question = cur.execute(f"SELECT COUNT(user_id) FROM users WHERE user_id='{random_follower_id}'").fetchone()

    print('is in database object', is_in_database_question)

    if is_in_database_question[0] == 0:
        print("user was not in user database moving onto new random user...")
        return False
    else:
        print("user was in database")
        return True


def make_connected_neighborhood():
    try:
        cur.execute('''CREATE TABLE new_users (user_id BIGINT, username)''')
        cur.execute('''CREATE TABLE new_followers (user_id, follower_id)''')
        print('succefully created new tables ')
    except Exception:
        print("new tables already exist ", Exception)

    initial_user = 132321192
    print("INITIAL USER: KEV", initial_user)
    random_follower = get_random_follower(initial_user)
    random_follower_id = random_follower[0]
    print("INITIAL RAND USER ID", random_follower_id, '\n\n')
    new_user_count = 0
    while new_user_count < 500:
        while not is_in_database(random_follower_id):
            random_follower_id = get_random_follower(initial_user)
            print('while loop random follower ids: ', random_follower_id)
        cur.execute('''INSERT INTO new_followers VALUES(?, ?)''', (initial_user, random_follower_id))
        user = cur.execute(f"SELECT * FROM users WHERE user_id={initial_user}").fetchone()
        print("user object", user, 'first ele', user[0], 'second ele', user[1])
        cur.execute('''INSERT INTO new_users VALUES(?, ?)''', (user[0], user[1]))

        con.commit()
        initial_user = random_follower_id
        random_follower_id = get_random_follower(initial_user)[0]
        new_user_count = new_user_count + 1
        print("count: ", new_user_count)


def add_nodes_to_new_graph():
    G = nx.DiGraph()
    users = cur.execute(f"SELECT * FROM users").fetchall()

    count = 0
    for user_id, user_name in users:
        if count == 2:
            break
        followers_of_user = cur.execute(f"SELECT * FROM followers WHERE user_id={user_id}").fetchall()
        # print('followers of user', followers_of_user)
        # print('user_id: ', user_id,' user_name: ', user_name)
        for userId, follower in followers_of_user:
            print("follower: ", follower)
            G.add_edge(follower, user_id)
        count = count + 1

    # net.from_nx(G)
    # net.show('social graph')
    nx.readwrite.write_edgelist(G, 'hamGraph.csv')


def make_better_graph():
    try:
        cur.execute('''CREATE TABLE new_new_users (user_id BIGINT, username)''')
        cur.execute('''CREATE TABLE new_new_followers (user_id, follower_id)''')
        print('succefully created new tables ')
    except Exception:
        print("new tables already exist ", Exception)

    users = cur.execute("SELECT * FROM users").fetchall();
    print('users ', users)
    for user_id, user_name in users:
        followers = cur.execute(f"SELECT * FROM followers WHERE user_id={user_id}").fetchall()
        #print('followers: ', followers)
        for parent, follower_id in followers:
            follower_in_users = cur.execute(f"SELECT COUNT(*) FROM users WHERE user_id='{follower_id}'").fetchone()
            # print('parent ', parent)
            # print('follower_in_users', follower_in_users)
            print('number returned? ', follower_in_users[0])
            # if follower_in_users[0] == 1:
            #     cur.execute("INSERT INTO new_new_followers VALUES(?, ?)", (user_id, follower_id))
            #     con.commit()
            #     print('inserted into new_new_followers: ', user_id, ":", user_name, ' and ', follower_id)


def draw_better_graph():
    G = nx.DiGraph()
    users = cur.execute(f"SELECT * FROM users").fetchall()

    count = 0
    for user_id, user_name in users:
        followers_of_user = cur.execute(f"SELECT * FROM new_new_followers WHERE user_id={user_id}").fetchall()
        # print('followers of user', followers_of_user)
        # print('user_id: ', user_id,' user_name: ', user_name)
        for userId, follower in followers_of_user:
            #print("follower: ", follower)
            G.add_edge(follower, user_id)

    node_list = list(G.nodes)
    matrix = nx.adjacency_matrix(G, nodelist=node_list).todense()
    matrix = matrix.transpose()
    #print("adjacency matrix \n", matrix)

    A = matrix.sum(axis=0).astype(float)
    #print("A matrix: \n", A)
    normalised_matrix = matrix / A

    #print('normalized matrix \n', normalised_matrix)
    R = np.full((1, 656), 1/656).transpose()
    #print('this is test R: ', R)

    count = 0
    while count != 100:
        #print('ITERATION:', count, ':: \n')
        R_plus_one = normalised_matrix * R
        diff_vector = np.subtract(R_plus_one, R)

        for index, num in enumerate(R_plus_one):
            print(isclose(num, R[index], abs_tol=1e-5))

        abs_diff_vector = np.abs(diff_vector)
        #print('diff vector::: ', abs_diff_vector)
        R = R_plus_one
        count = count + 1

    new_list = []
    for idx, name in enumerate(node_list):
        print('node    ', '    page rank     ')
        print(name, '          ', R[idx])
        new_list.append((name, R[idx]))

    sorted_new_list = sorted(new_list, key=lambda x: x[1], reverse=True)
    print("sorted new list ", sorted_new_list)
    #print('R matrix:: \n', R)




def test_page_rank():
    G = nx.DiGraph()
    G.add_edge('A', 'B')
    G.add_edge('B', 'A')
    G.add_edge('A', 'C')
    G.add_edge('A', 'D')
    G.add_edge('B', 'D')
    G.add_edge('D', 'B')
    G.add_edge('C', 'D')
    G.add_edge('D', 'C')

    node_list = list(G.nodes)
    matrix = nx.adjacency_matrix(G, nodelist=node_list).todense()
    matrix = matrix.transpose()
    print("adjacency matrix \n", matrix)

    A = matrix.sum(axis=0).astype(float)
    print("A matrix: \n", A)
    normalised_matrix = matrix / A

    print('normalized matrix \n', normalised_matrix)
    R = np.full((1, 4), 1/4).transpose()
    print('this is test R: ', R)

    count = 0
    while count != 30:
        R = normalised_matrix * R
        count = count + 1
        #print(count, " normalized matrix after iterations::: \n", normalised_matrix)
        print(count, " R matrix \n", R)



# def page_rank():
#     number_of_nodes = count_rows();
#     print('number of nodes ', number_of_nodes)
#
#     #now we need to make the probability matrix
#     zero_matrix = np.zeros(430336).reshape(656, 656)
#     print(zero_matrix)
#
#     users = cur.execute(f"SELECT * FROM users").fetchall()
#     for index_x, user_tuple in enumerate(users):
#         followers_of_user = cur.execute(f"SELECT * FROM new_new_followers WHERE user_id={user_tuple[0]}").fetchall()
#         follower_count = cur.execute(f"SELECT COUNT(*) FROM new_new_followers WHERE user_id={user_tuple[0]}").fetchone()[0]
#         for index_y, follower_tuple in enumerate(followers_of_user):
#             zero_matrix[index_y][index_x] = 1 / follower_count

    # print('zero matrix after the thing: \n', zero_matrix)


#count_rows();
# find_idless_user()
#createDataBase()
# test_database(132321192)
#seed_user_followers(seed_user_screen_name="KevinMBransford")
#get_random_follower(132321192)
#loop_and_grow()
#add_nodes_to_graph()
#make_connected_neighborhood()
# make_better_graph()
draw_better_graph()
# page_rank()
#test_page_rank()

# a = 1.0
# b = 1.00000001
# is_it_close = isclose(a, b, abs_tol=1e-4)
# print("is it close yoyoyo: : :: , ", is_it_close)

# def get_screen_name(id):
#     user_object = api.get_user(user_id=id)
#     print("screen name: ", user_object.screen_name)
#
# get_screen_name(22401067)
# get_screen_name(54122272)
# get_screen_name(28362043)
# get_screen_name(17121244)
# get_screen_name(1232468167)

get_random_follower(132321192)





