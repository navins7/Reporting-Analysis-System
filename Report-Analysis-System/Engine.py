#!/usr/bin/env python
import pymysql
import re, operator, sys, os
from nltk.tag import pos_tag


# import MySQLdb



debug = False
test = True


def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False


def load_stop_words(stop_word_file):
    stop_words = []
    for line in open(stop_word_file):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word)
    return stop_words


def separate_words(text, min_word_return_size):
    splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
    words = []
    for single_word in splitter.split(text):
        current_word = single_word.strip().lower()
        #leave numbers in phrase, but don't count as words, since they tend to invalidate scores of their phrases
        if len(current_word) > min_word_return_size and current_word != '' and not is_number(current_word):
            words.append(current_word)
    return words


def split_sentences(text):
    sentence_delimiters = re.compile(u'[.!?,;:\t\\\\"\\(\\)\\\'\u2019\u2013]|\\s\\-\\s')
    sentences = sentence_delimiters.split(text)
    return sentences


def build_stop_word_regex(stop_word_file_path):
    stop_word_list = load_stop_words(stop_word_file_path)
    stop_word_regex_list = []
    for word in stop_word_list:
        word_regex = r'\b' + word + r'(?![\w-])'  # added look ahead for hyphen
        stop_word_regex_list.append(word_regex)
    stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
    return stop_word_pattern


def generate_candidate_keywords(sentence_list, stopword_pattern):
    phrase_list = []
    for s in sentence_list:
        tmp = re.sub(stopword_pattern, '|', s.strip())
        phrases = tmp.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if phrase != "":
                phrase_list.append(phrase)
    return phrase_list


def calculate_word_scores(phraseList):
    word_frequency = {}
    word_degree = {}
    for phrase in phraseList:
        word_list = separate_words(phrase, 0)
        word_list_length = len(word_list)
        word_list_degree = word_list_length - 1
        for word in word_list:
            word_frequency.setdefault(word, 0)
            word_frequency[word] += 1
            word_degree.setdefault(word, 0)
            word_degree[word] += word_list_degree
    for item in word_frequency:
        word_degree[item] = word_degree[item] + word_frequency[item]

    word_score = {}
    for item in word_frequency:
        word_score.setdefault(item, 0)
        word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)

    return word_score


def generate_candidate_keyword_scores(phrase_list, word_score):
    keyword_candidates = {}
    for phrase in phrase_list:
        keyword_candidates.setdefault(phrase, 0)
        word_list = separate_words(phrase, 0)
        candidate_score = 0
        for word in word_list:
            candidate_score += word_score[word]
        keyword_candidates[phrase] = candidate_score
    return keyword_candidates


class Rake(object):
    def __init__(self, stop_words_path):
        self.stop_words_path = stop_words_path
        self.__stop_words_pattern = build_stop_word_regex(stop_words_path)

    def run(self, text):
        sentence_list = split_sentences(text)

        phrase_list = generate_candidate_keywords(sentence_list, self.__stop_words_pattern)

        word_scores = calculate_word_scores(phrase_list)

        keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores)

        sorted_keywords = sorted(keyword_candidates.items(), key=operator.itemgetter(1), reverse=True)
        return sorted_keywords

def main():
    if test:
        text = sys.argv[1]
        sentenceList = split_sentences(text)
        stoppath = "Stop_Word_List.txt"
        stopwordpattern = build_stop_word_regex(stoppath)

        phraseList = generate_candidate_keywords(sentenceList, stopwordpattern)
        wordscores = calculate_word_scores(phraseList)
        keywordcandidates = generate_candidate_keyword_scores(phraseList, wordscores)

        if debug: print (keywordcandidates)
        sortedKeywords = sorted(keywordcandidates.items(), key=operator.itemgetter(1), reverse=True)

        if debug: print (sortedKeywords)

        totalKeywords = len(sortedKeywords)
        if debug:
            print (sortedKeywords[0:int(totalKeywords / 3)])

        rake = Rake("Stop_Word_List.txt")
        keywords = rake.run(text)
        os.system("cls")
        print ("Issue(s) Relation: ", keywords)
        return(str(keywords))

if __name__ == '__main__':
    str = main()
    servername = "localhost";
    username= "root";
    password= "";
    dbname="repo";
    # Connect to the database
    con = pymysql.connect(host=servername, user=username, password=password,db=dbname)

    with con:
        cur = con.cursor()
        query_ = "INSERT INTO register (message) VALUES (%s)"
        cur.execute(query_,(sys.argv[1]))


    Checklist = [
                    "water",
                    "electricity",
                    "bathroom",
                    "maintainance",
                    "abusing",
                    "fees",
                    "teaching"
                ]

    category = "others"
    for word in Checklist:
            #print(category, word)
            if(word in str):
                category = word

    category = category.title()
    print("Category: ", category)

    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM register")
        rows = cur.fetchall()
        print(rows)

    # category = "Water"

    with con:
        cur = con.cursor()
        query_ = "UPDATE `result` SET severity = severity+1 WHERE category=%s"
        # query_ = "INSERT INTO result (category, severity) VALUES (%s , %s)"
        cur.execute(query_,(category))
