import psycopg2
import threading
import time

parameters = {
    "dbname": "",
    "user": "",
    "password": "",
}

def init_db():
    #Скидаємо попередні значення для кожної реалізації
    link = psycopg2.connect(**parameters)
    cur = link.cursor()
    cur.execute("UPDATE user_counter SET counter = 0, version = 0 WHERE user_id = 1;")
    link.commit()
    cur.close()
    link.close()

class Timer:
    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start

#_________________________________________________________________________________________________

def lost_update():
    link = psycopg2.connect(**parameters)  
    cur = link.cursor()  
    for _ in range(10_000):
        cur.execute("SELECT counter FROM user_counter WHERE user_id = 1")
        counter = cur.fetchone()[0] + 1
        cur.execute("UPDATE user_counter SET counter = %s WHERE user_id = 1", (counter,))
        cur.connection.commit()
    cur.close()
    link.close()

def in_place_update(cursor):
    for _ in range(10_000):
        cursor.execute("UPDATE user_counter SET counter = counter + 1 WHERE user_id = 1")
        cursor.connection.commit()

def select_for_update():
    link = psycopg2.connect(**parameters)  
    cur = link.cursor()  
    for _ in range(10_000):
        cur.execute("SELECT counter FROM user_counter WHERE user_id = 1 FOR UPDATE")  
        counter = cur.fetchone()[0] + 1
        cur.execute("UPDATE user_counter SET counter = %s WHERE user_id = 1", (counter,))
        link.commit()
    cur.close()
    link.close()

def optimistic_concurrency_control():
    link = psycopg2.connect(**parameters)  
    cur = link.cursor()  
    for _ in range(10_000):
        while True:
            cur.execute("SELECT counter, version FROM user_counter WHERE user_id = 1")
            
            result = cur.fetchone()
            counter, version = result

            counter += 1
            cur.execute("""
                UPDATE user_counter
                SET counter = %s, version = %s
                WHERE user_id = %s AND version = %s
            """, (counter, version + 1, 1, version))

            cur.connection.commit()
            if cur.rowcount > 0:
                break  
    cur.close()
    link.close()

def run(name):
    threads = [threading.Thread(target=name) for _ in range(10)]
    with Timer() as t:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    print(f"{name.__name__} execution time: {t.interval:.2f} seconds")

def run_in_place_update():
    conn = psycopg2.connect(**parameters)
    
    local_data = threading.local()
    local_data.connection = conn
    local_data.cursor = conn.cursor()

    threads = [threading.Thread(target=in_place_update, args=(local_data.cursor,)) for _ in range(10)]  

    with Timer() as t:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    local_data.cursor.close()
    local_data.connection.close()

    print(f"In-place update execution time: {t.interval:.2f} seconds")

if __name__ == "__main__":
    init_db()
    print("________________________________________________\n")
    run_in_place_update()
    print("\n______________________________________________\n")