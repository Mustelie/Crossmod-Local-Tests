import requests
import json
import csv
import time

input_file_name = 'crossmoddb_48hours_test_2'

csv_file_read = open(input_file_name + '.csv', 'r', encoding='utf8')

input_schema = ['created_at',
                'ingested_at',
                'comment_id',
                'comment_body',
                'toxicity_score',
                'crossmod_action',
                'author',
                'subreddit',
                'banned_by',
                'banned_at']

csv_reader = csv.DictReader(csv_file_read, fieldnames=input_schema)


def make_request(comment_id):
    url = 'https://www.reddit.com/api/info.json?id={}'.format('t1_' + comment_id)
    response = requests.get(url, headers={'User-agent': 'your bot 0.1'})
    comment = json.loads(response.text)

    return comment


def is_actually_removed(comment):
    # print(comment)
    try:
        author = comment['data']['children'][0]['data']['author']
        comment_body = comment['data']['children'][0]['data']['body']
        if author == '[deleted]' and comment_body == '[removed]':
            return True
        else:
            return False
    except:
        return False


header_row = False

unsorted_condensed = []
comments_actually_removed = 0
for row in csv_reader:
    comment_id = row['comment_id']

    ninety_plus = []
    ninety_plus_removed = 0
    eighty_to_ninety = []
    eighty_to_ninety_removed = 0
    seventy_to_eighty = []
    seventy_to_eighty_removed = 0
    try:
        if float(row['toxicity_score']) >= .70:
            comment = make_request(comment_id)
            actual_action = 'removed'
            if is_actually_removed(comment):
                comments_actually_removed += 1
                actual_action = 'removed'
            else:
                actual_action = 'not_removed'
            new_row = [comment_id, 'crossmod_' + row['crossmod_action'], row['toxicity_score'],
                       actual_action, row['comment_body'].replace('\n', ' ').replace('\r', ' ')]
            print(new_row)
            if float(row['toxicity_score']) >= .90:
                ninety_plus_removed += 1
                ninety_plus += new_row
            elif float(row['toxicity_score']) >= .80:
                eighty_to_ninety_removed += 1
                eighty_to_ninety += new_row
            else:
                seventy_to_eighty_removed += 1
                seventy_to_eighty += new_row
        else:
            continue
    except:
        continue
    time.sleep(0.05)


def calc_removal_ratio(row_list, num_removed):
    comments_actually_removed = 0
    for row in row_list:
        comment_id = row[0]
        comment = make_request(comment_id)
        if is_actually_removed(comment):
            comments_actually_removed += 1
    try:
        return comments_actually_removed / num_removed
    except:
        return 0


ninety_plus.sort(key=lambda x: float(x[2]), reverse=True)
eighty_to_ninety.sort(key=lambda x: float(x[2]), reverse=True)
seventy_to_eighty.sort(key=lambda x: float(x[2]), reverse=True)

unsorted_condensed.sort(key=lambda x: float(x[2]))
# print(unsorted_condensed)
for ninety in ninety_plus:
    print("{},{},{},{},\"{}\"".format(ninety[0], 'crossmod_' + ninety[1], ninety[2],
                                      ninety[3], ninety[4]))
print("Number of comments over the 90% toxicity threshold: {}".format(len(ninety_plus)))
print("Number of comments over the 90% toxicity threshold actually removed: {}".format(ninety_plus_removed))
print("Percentage of comments over the 90% toxicity threshold actually removed: {}".format(
    calc_removal_ratio(ninety_plus, ninety_plus_removed)))
for eighty in eighty_to_ninety:
    print("{},{},{},{},\"{}\"".format(eighty[0], 'crossmod_' + eighty[1], eighty[2],
                                      eighty[3], eighty[4]))
print("Number of comments over the 80% toxicity threshold: {}".format(len(eighty_to_ninety)))
print("Number of comments over the 80% toxicity threshold actually removed: {}".format(eighty_to_ninety_removed))
print("Percentage of comments over the 80% toxicity threshold actually removed: {}".format(
    calc_removal_ratio(eighty_to_ninety, eighty_to_ninety_removed)))
for seventy in seventy_to_eighty:
    print("{},{},{},{},\"{}\"".format(seventy[0], 'crossmod_' + seventy[1], seventy[2],
                                      seventy[3], seventy[4]))
print("Number of comments over the 70% toxicity threshold: {}".format(len(seventy_to_eighty)))
print("Number of comments over the 70% toxicity threshold actually removed: {}".format(seventy_to_eighty_removed))
print("Percentage of comments over the 70% toxicity threshold actually removed: {}".format(
    calc_removal_ratio(seventy_to_eighty, seventy_to_eighty_removed)))
#
# print()
# print()
# print()
# print('-----')
# print("Total number removed by Crossmod: {}".format(comments_removed_by_crossmod))
# print("Total number actually removed: {}".format(comments_actually_removed))
# print("Overall percentage: ", str(comments_actually_removed / comments_removed_by_crossmod))
