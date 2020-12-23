import json
import shutil
import tempfile
import os

def process(id, name):
path = 'data/' + id[0:3] + '/' + id[3:6] + '/' + id[
6:] + '/' + id + '.geojson'
print(path)

	data = json.load(open(path))

	data["properties"]['wof:lastmodified'] = 1592331253
	data["properties"]["name:eng_x_variant"] = [
			name, "%s Township" % name,
			"%s Charter Township" % name
	]
	data["properties"]["name:eng_x_preferred_longname"] = [
			"%s Charter Township" % name
	]
	data["properties"]["name:eng_x_preferred_placetype"] = ['charter township']

	
	newfile = tempfile.NamedTemporaryFile(delete=False)
	newfile.write(json.dumps(data).encode('utf-8'))
	newfile.close()
	os.system(f'cat {newfile.name} | docker run -i whosonfirst-exportify /usr/local/bin/wof-exportify -e stdout --stdin > {path}')
	
	print(newfile.name)
