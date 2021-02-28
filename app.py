from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

from time import sleep

import geckodriver_autoinstaller

FACEBOOK_MAIL = 'josef.utbult@hotmail.com'
FACEBOOK_PSWD = '@orSmn!9L$nCv#'

def wait(driver, xpath):
	try:
	    myElem = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
	except TimeoutException:
	    print("Loading page took to long")
	    return


def login(driver):
	driver.get('https://www.facebook.com/messages')
	assert 'Facebook' in driver.title

	# Login
	elem = driver.find_element_by_xpath('//*[@id="email"]')
	elem.clear()
	elem.send_keys(FACEBOOK_MAIL)

	elem = driver.find_element_by_xpath('//*[@id="pass"]')
	elem.clear()
	elem.send_keys(FACEBOOK_PSWD)

	elem.send_keys(Keys.RETURN)


'''
Return example:

{
	sender: name,
	content: [
		{
			type: text,
			data: Here is the message
		}
	]
}
'''
def get_last_message(driver):
	while True:
		chat_xpath =  							'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[1]/div/div/div/div[3]/div[1]/div[2]/div/div/div[{i}]/div/div[1]/div/a'
		contact_messages_container_xpath = 		'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div/div[1]/div[1]/div/div/div[3]/div'
		messages_container_xpath = 				'/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/div/div/div/div/div[1]/div[2]/div/div/div/div[1]/div[1]/div/div/div[3]/div/div'

		relative_sender_info_xpath = 			'/div[2]/div[7]/div/div/div/div[1]/span/div/span/div'
		relative_message_text_content_path = 	'/div/div/div/div[2]/span/div/div/div/div'
		relative_message_image_path = 			'/div/div/div/div[2]/span/div/div/div/div/a/img'
		relative_message_emoji_path =			'/div/div/div/div[2]/span/div/div/div/span/img'

		# Load latest chat
		wait(driver, chat_xpath.format(i = 1))
		elem = driver.find_element_by_xpath(chat_xpath.format(i = 1))
		elem.send_keys(Keys.RETURN)

		# Get last message
		wait(driver, contact_messages_container_xpath)
		elements = driver.find_elements_by_xpath(messages_container_xpath)
		while(len(elements) <= 2):
			elements = driver.find_elements_by_xpath(messages_container_xpath)

		print(len(elements[-1].find_elements_by_tag_name('div')))
		last_element = driver.find_elements_by_xpath(messages_container_xpath + f'[{len(elements)}]/div[2]/div')[-1]

		try:
			sender = elements[-1].get_attribute('innerText').split('\n')[0]
		except NoSuchElementException:
			sender = 'None'

		output = {
			'sender': sender,
			'content': []
		}
		
		if len(last_element.get_attribute('innerText').split('\n')) > 1:
			output['content'].append({'type': 'text', 'data': last_element.get_attribute('innerText').split('\n')[1]})

		images = last_element.find_elements_by_tag_name('img')
		for image in images:
			output['content'].append({'type': 'image', 'data': image.get_attribute('src')})

		return output
		

		# Extract sender
		try:
			sender = elements[-1].get_attribute('innerText').split('\n')[0]
		except NoSuchElementException:
			sender = 'None'

		# Check if image
		try:
			element = driver.find_element_by_xpath(last_element_xpath + relative_message_image_path)
			return {
				'sender': sender,
				'content': [
					{
						'type': 'image',
						'data': element.get_attribute('src')
					}
				]
			}
		except NoSuchElementException:
			pass

		# Check if emoji
		elements = driver.find_elements_by_xpath(last_element_xpath + relative_message_emoji_path)
		if elements:
			return {
				'sender': sender,
				'content': [ {'type': 'image', 'data': current.get_attribute('src')} for current in elements]
			}

		# Check if text
		try:
			element = driver.find_element_by_xpath(last_element_xpath + relative_message_text_content_path)
			return {
				'sender': sender,
				'content': [
					{
						'type': 'text',
						'data': element.get_attribute('innerText')
					}
				]
			}
		except NoSuchElementException:
			return {
				'sender': 'none',
				'content': [
					{
						'type': 'text',
						'data': 'Some kind of nonsense'
					}
				]
			} 


def main():
	geckodriver_autoinstaller.install()

	driver = webdriver.Firefox()
	login(driver)

	try:		
		while True:
			msg = get_last_message(driver)
			print(msg)
			input()

	except KeyboardInterrupt:
		pass

main()