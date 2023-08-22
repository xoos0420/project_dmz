import pandas as pd
import torch
import string
import DAO
import predict_fn

from transformers import BertTokenizerFast, BertForSequenceClassification

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
        print(word_replacements.items())
        if word in already_replaced:
            continue
        new_sentences = []
        for sent in sentences:
            if word in sent:
                replacement_words = []
                for replacement in replacements[1:]:
                    new_sentence = sent.replace(word, replacement)
                    print(new_sentence)
                    replacement_words.append(replacement)
                    # print(replacement_words)
                    new_sentences.append(new_sentence)
                    already_replaced.add(replacement)
                    # 만약 새로운 대체어가 다시 신조어를 포함하고 있다면, 해당 신조어도 추가
                    for replaced_word, replaced_replacements in word_replacements.items():
                        if replaced_word != word and replaced_word in replacement:
                            already_replaced.add(replaced_word)
            else:
                new_sentences.append(sent)
        sentences = new_sentences
    return sentences, replacement_words

def evaluate_naturalness(replaced_sentences):
    tokenizer = BertTokenizerFast.from_pretrained('klue/bert-base')
    model = BertForSequenceClassification.from_pretrained('klue/bert-base')

    max_naturalness_score = -1
    most_natural_sentence = None

    for i in range(len(replaced_sentences)):
        for j in range(i+1, len(replaced_sentences)):
            sentence1 = replaced_sentences[i]
            print(sentence1)
            sentence2 = replaced_sentences[j]
            print(sentence2)
            inputs = tokenizer(sentence1, sentence2, add_special_tokens=True, return_tensors='pt', truncation=True, padding=True)
            with torch.no_grad():
                outputs = model(**inputs)
            logits = outputs.logits
            prob = torch.softmax(logits, dim=1)
            similarity_score = prob[:, 1].item()
            print(similarity_score)
            print('-------------')
            if similarity_score > max_naturalness_score:
                max_naturalness_score = similarity_score
                most_natural_sentence = sentence1 if similarity_score > 0.5 else sentence2
    return most_natural_sentence

def mask(sentences, replacement_words):
    masked_sentences = []
    for sent in sentences:
        for word in replacement_words:
            if word in sent:
                word_idx = sent.index(word)
                try:
                    replace_mask = sent[word_idx + len(word)]
                except IndexError:
                    replace_mask = ""

                if replace_mask.strip() and replace_mask.isalnum():
                    mask = sent[:word_idx + len(word)] + '<mask>' + sent[word_idx + len(word)+1:]
                    masked_sentences.append(mask)
                else:
                    masked_sentences.append(sent)

    return masked_sentences

def predict_mask(masked_sentences):
    predictions = []

    for sentence in masked_sentences:
        if '<mask>' in sentence:
            prediction = predict_fn.predict(sentence)
            predictions.append(prediction)
        else:
            predictions.append('None')

    return predictions

def replace_mask(masked_sentences, predictions):
    replaced_sentences = []

    for sentence, prediction in zip(masked_sentences, predictions):
        if '<mask>' in sentence:
            if prediction != 'None':
                # <mask>를 예측된 단어로 치환
                for key, value in prediction.items():
                    words_to_replace = value.split(' / ')
                    for word in words_to_replace:
                        replaced_sentence = sentence.replace('<mask>', word)
                        replaced_sentences.append(replaced_sentence)
            else:
                replaced_sentences.append(sentence)
        else:
            replaced_sentences.append(sentence)

    return replaced_sentences

def main(sentence, cur):
    word_replacements = get_word_replacements(sentence, cur)
    found_words = check_word_in_sentence(sentence, word_replacements.keys())
    return_1= get_id(word_replacements)

    if found_words:
        print(f"신조어: {', '.join(found_words)}")
        replaced_sentences, replacement_words = replace_words(sentence, word_replacements)
        for i, sentence in enumerate(replaced_sentences, 1):
            print(f"{i}. 번역 결과: {sentence}")

            masked_sentences = mask(replaced_sentences, replacement_words)

            predictions = predict_mask(masked_sentences)

            replaced_sentences1 = replace_mask(masked_sentences, predictions)
            print(f"{i}. 치환 결과: {replaced_sentences1}")

        if len(replaced_sentences1) > 1:
            most_natural_sentence = evaluate_naturalness(replaced_sentences1)
            print(f"가장 자연스러운 문장: {most_natural_sentence}")
        else:
            most_natural_sentence = replaced_sentences1

        for idx, found_word in enumerate(found_words, 1):
            print(f"해석 {idx}. {found_word} : {word_replacements[found_word][0]}")  # 해당 신조어의 해석 출력
    
    else:
        print("입력한 문장에 설정된 단어가 포함되어 있지 않습니다.")
        found_word = 0
        word_replacements[found_word] = ['신조어가 포함된 문장을 입력해주세요']
        found_words = '신조어가 포함된 문장이 없습니다'
        most_natural_sentence = '위 예시를 참고해주세요'
        a = '신조어가 없습니다'

        return None,None,None

    return list(return_1.keys()) if return_1 else a, list(return_1.values()), most_natural_sentence
if __name__ == "__main__":
    main()