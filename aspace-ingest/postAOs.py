import json, requests, csv, time, secrets

startTime = time.time()

# import secrets
baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

# test for successful connection
def test_connection():
	try:
		requests.get(baseURL)
		print 'Connected!'
		return True

	except requests.exceptions.ConnectionError:
		print 'Connection error. Please confirm ArchivesSpace is running.  Trying again in 10 seconds.'

is_connected = test_connection()

while not is_connected:
	time.sleep(10)
	is_connected = test_connection()

#authenticate
auth = requests.post(baseURL + '/users/'+user+'/login?password='+password).json()
session = auth["session"]
headers = {'X-ArchivesSpace-Session':session, 'Content_Type':'application/json'}

# User supplied variables
ao_csv = raw_input('Enter csv filename: ')
resource_record = raw_input('Enter resource record uri: ')
parent_series = raw_input('Enter parent series uri: ')

# Open csv, create new csv
csv_dict = csv.DictReader(open(ao_csv))
f=csv.writer(open('new_' + ao_csv, 'wb'))
f.writerow(['title']+['dateBegin']+['uri'])

# Construct JSON to post from csv
aoList = []
for row in csv_dict:
	# variables
	title = row['title']
	subject_1 = row['subject1']
	subject_2 = row['subject2']
	date_expression = row['dateExpression']
	date_begin = row['dateBegin']
	agent_2 = row['agentRef2']
	agent_3 = row['agentRef3']
	first_top_container = row['top_container_1']
	first_indicator_1 = row['Box1']
	first_indicator_2 = row['Disc1']
	second_top_container = row['top_container_2']
	second_indicator_1 = row['Box2']
	second_indicator_2 = row['Disc2']
	third_top_container = row['top_container_3']
	third_indicator_1 = row['Box3']
	third_indicator_2 = row['Disc3']
	fourth_top_container = row['top_container_4']
	fourth_indicator_1 = row['Box4']
	fourth_indicator_2 = row['Disc4']	
	digital_object = row['digital_object']
	# construct JSON
	aoRecord = {'publish': False, 'title': title, 'level': 'file'}
	# subjects
	if not subject_1 == '' and not subject_2 == '':
		aoRecord['subjects'] = {'ref': subject_1}, {'ref': subject_2}
	elif not subject_1 == '' and subject_2 == '':
		aoRecord['subjects'] = {'ref': subject_1}
	else:
		pass
	# dates
	aoRecord['dates'] = [{'expression': date_expression, 'begin': date_begin, 'date_type': 'single', 'label': 'creation'}]
	# linked agents
	if not agent_2 == '' and not agent_3 == '':
		aoRecord['linked_agents'] = {'role': 'creator', 'relator': 'pht', 'ref': '/agents/corporate_entities/388'}, {'role': 'creator', 'relator': 'spn', 'ref': agent_2}, {'role': 'creator', 'relator': 'spn', 'ref': agent_3}
	elif not agent_2 == '' and agent_3 == '':
		aoRecord['linked_agents'] = {'role': 'creator', 'relator': 'pht', 'ref': '/agents/corporate_entities/388'}, {'role': 'creator', 'relator': 'spn', 'ref': agent_2}
	else:
		aoRecord['linked_agents'] = [{'role': 'creator', 'relator': 'pht', 'ref': '/agents/corporate_entities/388'}]
	# Start instances
	## Homewood Photo use case assumes there may be up to 3 physical containers and 1 digital object instance
	instances = []
	# first instance
	if not first_top_container == '':
		container = {'type_1': 'box', 'indicator_1': first_indicator_1, 'type_2': 'item', 'indicator_2': first_indicator_2}
		sub_container = {'type_2': 'item', 'indicator_2': first_indicator_2}
		sub_container['top_container'] = {'ref': first_top_container}
		instance_1 = {'instance_type': 'mixed_materials', 'sub_container': sub_container, 'container': container}
		instances.append(instance_1)
	# second instance
	if not second_top_container == '':
 		container = {'type_1': 'box', 'indicator_1': second_indicator_1, 'type_2': 'item', 'indicator_2': second_indicator_2}
		sub_container = {'type_2': 'item', 'indicator_2': second_indicator_2}
		sub_container['top_container'] = {'ref': second_top_container}
		instance_2 = {'instance_type': 'mixed_materials', 'sub_container': sub_container, 'container': container}
		instances.append(instance_2)
	# third instance
	if not third_top_container == '':
 		container = {'type_1': 'box', 'indicator_1': third_indicator_1, 'type_2': 'item', 'indicator_2': third_indicator_2}
		sub_container = {'type_2': 'item', 'indicator_2': third_indicator_2}
		sub_container['top_container'] = {'ref': third_top_container}
		instance_3 = {'instance_type': 'mixed_materials', 'sub_container': sub_container, 'container': container}
		instances.append(instance_3)
	# fourth instance
	if not fourth_top_container == '':
 		container = {'type_1': 'box', 'indicator_1': fourth_indicator_1, 'type_2': 'item', 'indicator_2': fourth_indicator_2}
		sub_container = {'type_2': 'item', 'indicator_2': fourth_indicator_2}
		sub_container['top_container'] = {'ref': fourth_top_container}
		instance_4 = {'instance_type': 'mixed_materials', 'sub_container': sub_container, 'container': container}
		instances.append(instance_4)
	# digital objects
	if not digital_object =='':
		digital_object = {'ref': digital_object}
		digital_object_1 = {'instance_type': 'digital_object', 'digital_object': digital_object}
		instances.append(digital_object_1)
	# Finish up instances
	aoRecord['instances'] = instances
	# notes
	restriction_note = [{'jsonmodel_type': 'note_text', 'content': 'This digital content is available offline. Contact Special Collections for more information.', 'publish': True}]
	aoRecord['notes'] = [{'jsonmodel_type': 'note_multipart', 'type': 'accessrestrict', 'publish': True, 'subnotes': restriction_note}]
	# resource and parent
	# Note: needs to have a linked resource or else NoMethodError
	aoRecord['resource'] = {'ref': '/repositories/3/resources/' + resource_record}
	aoRecord['parent'] = {'ref': '/repositories/3/archival_objects/' + parent_series}
	aoRecord = json.dumps(aoRecord)
	post = requests.post(baseURL + '/repositories/'+ repository + '/archival_objects', headers=headers, data=aoRecord).json()
	print post
	# Save uri to new csv file
	uri = post['uri']
	f.writerow([title]+[date_begin]+[uri])

# Feedback to user
print 'New .csv saved to working directory.'

# show script runtime
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Post complete.  Total script run time: ', '%d:%02d:%02d' % (h, m, s)
