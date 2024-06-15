from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import redis
import json
import threading
from queue import Queue

def validateCpf(cpf, date):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://servicos.receita.fazenda.gov.br/Servicos/CPF/ConsultaSituacao/ConsultaPublica.asp")

    time.sleep(1)
    cpfInput = driver.find_element(By.XPATH, "//input[@id='txtCPF']")
    cpfInput.send_keys(cpf)

    dateInput = driver.find_element(By.XPATH, "//input[@id='txtDataNascimento']")
    dateInput.send_keys(date)

    element = driver.find_element(By.XPATH, "//div[@id='hcaptcha']")
    element.click()
    time.sleep(1.5)

    submit = driver.find_element(By.XPATH, "//input[@id='id_submit']")
    submit.click()

    time.sleep(0.5)

    spans = driver.find_elements(By.XPATH, "//span[@class='clConteudoDados']")
    data = {}
    
    for span in spans:
        text = span.text
        key, value = text.split(":")
        
        data[key.strip()] = value.strip()

    driver.switch_to.default_content()
    driver.quit()
    return data

def process_event(event):
    cpf = event['cpf']
    date = event['date']
    event_id = event['id']
    
    result = validateCpf(cpf, date)
    
    return {'id': event_id, 'data': result}

def consumer(queue, redis_client):
    while True:
        event = queue.get()
        
        result = process_event(event)
        
        redis_client.publish('processed_events', json.dumps(result))
        queue.task_done()

def main():
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    event_queue = Queue()
    
    for _ in range(3):
        t = threading.Thread(target=consumer, args=(event_queue, redis_client))
        t.daemon = True
        t.start()

    pubsub = redis_client.pubsub()
    pubsub.subscribe('incoming_events')
    for message in pubsub.listen():
        if message['type'] == 'message':
            event = json.loads(message['data'])
            event_queue.put(event)

if __name__ == "__main__":
    main()