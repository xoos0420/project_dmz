import random
#랜덤으로 3가지 가져오는거


def search_all(cur):
    sql = 'SELECT word,mean,similar from dmz.new_word;'
    cur.execute(sql)
    result = cur.fetchall()
    return result

def search_db(input,cur):
    sql = f'SELECT word,mean,similar FROM dmz.new_word WHERE word ="{input}";'
    cur.execute(sql)
    result = cur.fetchone()
    return result


def random_word(cur):
    random_numbers = [random.randint(1, 950) for _ in range(3)]
    sql = f'select word,mean,similar from dmz.new_word where number in ({", ".join(map(str, random_numbers))});'
    cur.execute(sql)
    result = cur.fetchall()
    return result

