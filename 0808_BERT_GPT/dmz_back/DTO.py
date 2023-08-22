# improve_sentence 미적용
# 재해석 문제 해결
# 다수의 해석이 있는 경우 해결

import os
import pandas as pd
from dotenv import load_dotenv
import DAO
from transformers import BertTokenizer, BertForSequenceClassification,XLMRobertaTokenizerFast,XLMRobertaForMaskedLM
import torch
import openai

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_ORGANIZATION = os.getenv('API_ORGANIZATION')

def get_id(word_replacements):
    return_dic = {}
    for i in list(word_replacements.keys()):
        return_dic[i] = word_replacements[i][0]
    return return_dic


def get_word_replacements(sentence,cur):
    word_replacements = {}
    result = DAO.search_all(cur)
    for i in result:
        if i[0] in sentence:
            synonyms = i[2].split(',')
            synonyms = [synonym.strip() for synonym in synonyms]
            word_replacements[i[0]] = [i[1]]+synonyms
    print(f'DTO에서 출력중 \n {word_replacements}')
    return word_replacements


# def get_mean(sentence,cur):
#     means = {}
#     result = DAO.search_all(cur)
#     for i in result:
#         if i[0] in sentence:
#             synonyms = i[2].split(',')
#             synonyms = [synonym.strip() for synonym in synonyms]
#             means[i[0]] = [i[1]] + synonyms
#     print(f'DTO에서 출력중 \n {means}')
#     return means



def check_word_in_sentence(sentence, word_list):
    found_words = []
    for word in word_list:
        if word in sentence:
            found_words.append(word)  # 캐치한 신조어를 리스트에 추가
    return found_words


def replace_words(sentence, word_replacements):
    sentences = [sentence]
    already_replaced = set()

    for word, replacements in word_replacements.items():
        if word in already_replaced:
            continue

        new_sentences = []
        for sent in sentences:
            if word in sent:
                for replacement in replacements[1:]:
                    new_sentence = sent.replace(word, replacement)
                    new_sentences.append(new_sentence)
                    already_replaced.add(replacement)

                    # 만약 새로운 대체어가 다시 신조어를 포함하고 있다면, 해당 신조어도 추가
                    for replaced_word, replaced_replacements in word_replacements.items():
                        if replaced_word != word and replaced_word in replacement:
                            already_replaced.add(replaced_word)
            else:
                new_sentences.append(sent)
        sentences = new_sentences

    return sentences



def evaluate_naturalness(sentence_list):
    tokenizer = BertTokenizer.from_pretrained('klue/bert-base')
    model = BertForSequenceClassification.from_pretrained('klue/bert-base')

    max_naturalness_score = -1
    most_natural_sentence = None

    for i in range(len(sentence_list)):
        for j in range(i+1, len(sentence_list)):
            sentence1 = sentence_list[i]
            sentence2 = sentence_list[j]

            inputs = tokenizer(sentence1, sentence2, add_special_tokens=True, return_tensors='pt', truncation=True, padding=True)

            with torch.no_grad():
                outputs = model(**inputs)

            logits = outputs.logits
            prob = torch.softmax(logits, dim=1)
            similarity_score = prob[:, 1].item()

            if similarity_score > max_naturalness_score:
                max_naturalness_score = similarity_score
                most_natural_sentence = sentence1 if similarity_score > 0.5 else sentence2

    return most_natural_sentence

def improve_sentence(sentence):
    openai.organization = API_ORGANIZATION
    openai.api_key = API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"{sentence} 를 자연스러운 문장으로 바꿔줘",
            },
        ]
    )

    bot_response = response['choices'][0]['message']['content']
    return bot_response

def main(sentence,cur):
    try:
        word_replacements = get_word_replacements(sentence,cur)
        return_1= get_id(word_replacements)
        means = list(return_1.values())
        user_input = sentence

        found_words = check_word_in_sentence(user_input, word_replacements.keys())
        if found_words:
            print(f"신조어: {', '.join(found_words)}")
            replaced_sentences = replace_words(user_input, word_replacements)
            for i, sentence in enumerate(replaced_sentences, 1):
                print(f"{i}. 번역 결과: {sentence}")

            if len(replaced_sentences) > 1:
                most_natural_sentence = evaluate_naturalness(replaced_sentences)
                print(f"가장 자연스러운 문장: {most_natural_sentence}")
                bot_response = improve_sentence(most_natural_sentence)
                print(f"GPT 변환문장: {bot_response}")
                super_most_natural_sentence = evaluate_naturalness((most_natural_sentence,bot_response))
                print(f"GPT VS 가장 자연스러운 문장:{super_most_natural_sentence}")
            else:
                bot_response = improve_sentence(replaced_sentences[0])
                print(f"GPT 변환문장: {bot_response}")
                super_most_natural_sentence = evaluate_naturalness((replaced_sentences[0], bot_response))
                print(f"GPT VS 가장 자연스러운 문장:{super_most_natural_sentence}")
            
                temp_1 = []
            for idx, found_word in enumerate(found_words, 1):
                print(f"해석 {idx}. {found_word} : {word_replacements[found_word][0]}")  # 해당 신조어의 해석 출력
                print(f'0804{found_word}')
                temp_1.append(word_replacements[found_word][0])
        else:
            return None, None, None
    except:
        print("==============================================")
    return found_words,means,super_most_natural_sentence