import tweepy
import yaml
import networkx as nx
import matplotlib.pyplot as plt
import json

# yaml file reader funtion
def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

# yaml config file path
file_path = "venv/twitter_api_key_config.yaml"
# read from config file
api_credential = read_yaml(file_path)

# API authentication
auth = tweepy.OAuthHandler(api_credential["api_key"], \
                           api_credential["api_secret_token"])
auth.set_access_token(api_credential["access_token"], \
                      api_credential["access_token_secret"])
api = tweepy.API(auth, wait_on_rate_limit=True)

DiGraph = nx.DiGraph();

def get_kevs_followers():
    ids = []
    for followers in api.get_follower_ids(screen_name="KevinMBransford", cursor=-1):
        ids.extend(followers)
    return ids;

def create_graph_from_kev(followers):
    DiGraph.add_nodes_from(followers)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    Kevin = api.get_user(screen_name="KevinMBransford")
    KevinID = Kevin.id;
    DiGraph.add_node(KevinID)
    kevinFollowersIDs = get_kevs_followers();
    DiGraph.add_nodes_from(kevinFollowersIDs);

    for followerID in kevinFollowersIDs:
        DiGraph.add_edge(followerID, KevinID)





    nx.draw(DiGraph)
    plt.show()
