import sys
sys.path.append('./copct-master')
import copct
from load_facility_demo import load_demo

def lookup_type(object_id, state):
	return [obj_type for (obj_id,obj_type,_,_,_,_) in state if obj_id == object_id][0]

def causes(v):
	states, actions, arguments = zip(*v)
	g = set()
	if actions == ('move-to',):
		object_id = arguments[0][0]
		object_type = lookup_type(object_id, states[0])
		if object_type == 'block':
			g.add((states[0],'stack',arguments[0][1]+arguments[0][2]+arguments[0][3]+arguments[0][4]+arguments[0][5]+arguments[0][0]))
	if actions == ('stack',):
		all_block = [obj_id for (obj_id, obj_type,_,_,_,_) in states[0] if obj_type == 'block']
		if set(all_block) == set(arguments[0][5]+arguments[0][6]+arguments[0][7]+arguments[0][8:]) and argument[0][0] == 'room':
			g.add((states[0],'stack-all',arguments[0][1]+arguments[0][2]+arguments[0][3]+arguments[0][4]))
	if actions == ('grasp','release',):
		g.add((states[0],'move-to',arguments[0][0]+arguments[1][1]+arguments[1][2]+arguments[1][3]+arguments[1][4]+arguments[1][5]))
	if actions == ('move-to','stack',):
		object_id = arguments[1][0]
		object_type = lookup_type(object_id, states[0])
		if object_type == 'block' and argument[0][0] == argument[1][0]:
			g.add((states[0],'stack',arguments[0][1]+arguments[0][2]+arguments[0][3]+arguments[0][4]+arguments[0][5]+arguments[1][0]+arguments[1][5]+arguments[1][6]+arguments[1][7:]))
	return g

M=2

if __name__=='__main__':

	# Load demo
	demo = load_demo(demo_directory='./SMILE-1.1.0/room_demo/')

	# interpret demo (fixed-parameter-tractable when M is small and explicitly provided)
	status, tlcovs, g = copct.explain(causes, demo, M=M)
	print('copct status: %s'%status)
	print('%d covers'%len(tlcovs))

	# get most parsimonious covers
	pcovs, length = copct.minCardinalityTLCovers(tlcovs)
	print('%d covers of length %d'%(len(pcovs), length))

	# Show the first one
	print('First cover of length %d:'%length)
	for intention in pcovs[0][0]:
		print(intention[1:])
