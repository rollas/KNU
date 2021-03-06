if __name__ == '__main__':
    print('Main Routine : Query')

import globals as gb
import analyze as an
import dump as dp
import math
from queue import PriorityQueue
import hangeul as hg

# weight table
w_table = dp.read(gb.f_pkl_w)

# query
query_input = '캅카'

# top K
topk = 5

# tolerant level
initial_tolerance = 1

# max edit distance
max_dist = 10000000

"""
# -------------------------- #
# ----- Document Vector----- #
# -------------------------- #
"""
#   doc_vectors = {
#       doc : [#, #, ..., #], (length of len(query extract)
#       ...
#   }


def get_doc_vector(tokens):
    doc_vectors = dict()

    n = len(tokens)

    for index, token in enumerate(tokens):
        if token not in w_table:
            continue

        # get document weight from table
        for doc, weight in w_table[token].items():

            # initialize vector
            if doc not in doc_vectors:
                doc_vectors[doc] = [0] * n

            # set weight
            doc_vectors[doc][index] = weight

    return doc_vectors


"""
# --------------------------------- #
# ----- Scoring & Top Results ----- #
# --------------------------------- #
"""


def score_and_tops(q_vector, doc_vectors, k, exclude=None):
    n = len(q_vector)

    # get scores & sort
    pq = PriorityQueue()
    for doc, vector in doc_vectors.items():

        # absolute value of document vector
        # ignore zero vector
        absolute = 0
        for element in vector:
            absolute += element
        if absolute == 0.0:
            continue
        absolute = math.sqrt(absolute)

        # dot product
        score = 0
        for i in range(n):
            score += q_vector[i] * vector[i]

        # divide by absolute value
        score /= absolute

        # push score
        pq.put((-score, doc))

        print('\tscore:', doc, [float("{:.4f}".format(x)) for x in vector], '=>', float("{:.4}".format(score)))

    # get top K results
    top = list()
    if exclude is not None:
        while pq.qsize() != 0:
            s, d = pq.get()
            bind = (d, -1 * s)
            if bind not in exclude:
                top.append(bind)
                if len(top) == k:
                    break
    else:
        while pq.qsize() != 0:
            s, d = pq.get()
            bind = (d, -1 * s)
            top.append(bind)
            if len(top) == k:
                break

    return top



"""
# ---------------------- #
# ----- Spellcheck ----- #
# ---------------------- #
"""
#   pq_dist :
#       list of PriorityQueue()
#       each of edit distances with each token


def get_distance_pq(tokens):
    pq_dist = []
    for index, token in enumerate(tokens):
        pq = PriorityQueue()
        for term in w_table.keys():
            dist = hg.edit_dist(token, term)
            pq.put((dist, index, term))
        pq_dist.append(pq)

    return pq_dist


"""
# ------------------------ #
# ----- Main Routine ----- #
# ------------------------ #
"""


def retrieve_top_k(query, k):

    tokens = an.s_extract(query)
    tokens = list(dict.fromkeys(tokens)) # drop duplicate tokens
    tokens_origin = tokens.copy()

    n = len(tokens)
    q_vector = [1] * n
    found = 0

    print('initial tokens:', tokens)

    pq_dist = get_distance_pq(tokens)

    # ------------------------------------------- #
    # Initial Tolerance for limited edit distance #
    # ------------------------------------------- #
    for index, pq in enumerate(pq_dist):
        dist = pq.queue[0][0]
        # correct token
        if dist == 0:
            pq.get()
        # tolerance on misspelled token
        elif dist <= initial_tolerance:
            term = pq.queue[0][2]
            tokens[index] = term
            pq.get()
        # no chance
        else:
            continue

    # ----------------- #
    # Initial Retrieval #
    # ----------------- #
    print('attempt 1 tokens:', tokens)

    # get vectors
    doc_vectors = get_doc_vector(tokens)

    # get top K results
    tops = score_and_tops(q_vector, doc_vectors, k)
    found = len(tops)
    print('attempt 1 ... found =', found)
    if found == k:
        return tops

    # now the case that results are less than K

    # ------------------ #
    # Tolerant Retrieval #
    # ------------------ #
    attempt = 2
    while True:
        # break : all PQueues are empty
        empty = True
        for pq in pq_dist:
            empty = empty and (pq.qsize() == 0)
        if empty:
            break

        # get one minimum element
        min_dist = max_dist
        min_index = -1
        for pq in pq_dist:
            dist, index, term = pq.queue[0]
            if (min_dist > dist)\
                or (min_dist == dist and len(tokens_origin[min_index]) < len(tokens_origin[index])):
                min_dist = dist
                min_index = index

        dist, index, term = pq_dist[min_index].get()

        # retrieve
        tokens[index] = term
        print('attempt', attempt, 'tokens:', tokens)
        doc_vectors = get_doc_vector(tokens)
        tops_rest = score_and_tops(q_vector, doc_vectors, k - found, tops)
        tops.extend(tops_rest)
        found = len(tops)
        print('attempt', attempt, 'found =', found)
        attempt += 1
        if found == k:
            break

    return tops


retrieved = retrieve_top_k(query_input, topk)
print()
print('----- found {}/{} results -----'.format(len(retrieved), topk))
for rank, tup in enumerate(retrieved):
    doc, score = tup
    print('#{}\t{} ... {:.4f}'.format(rank+1, doc, score))
