import csv
import re

debug = True

def get_cond_arg_indices(cond_arg, actions):
	i = 0
	for action in actions:
		j = 0
		for arg in action[1]:
			if (arg == cond_arg or (arg[:4] == 'CONT' and cond_arg[:4] == 'CONT')):
				return str(i),str(j)
			j+=1
		i+=1
	return str(-1), str(-1)

def parse_action(action):
	if debug: print "Parsing Action: ", action
	action_parse = re.findall(r'([a-z A-Z 0-9 \- \.]+)', action)
	name = action_parse[0]
	args_temp = action_parse[1:]
	args = []
	for arg in args_temp:
		args.append(arg.replace(' ', ''))
	if debug: 
		print '\tName: ', name
		print '\tArgs: ', args
	return name, args

def parse_cond(cond):
	if debug: print "Parsing Condition: ", cond
	cond_parsed = [[]]
	index = 0
	for i in range(0, len(cond)):
		# TODO: BINDING ON OR IS WRONG!!!
		if (cond[i] == 'or'):
			cond_parsed.append([])
			index += 1
		else:
			all_cond = re.match(r'all\(([a-z A-Z 0-9 \- \']+)\)', cond[i])
			eq_cond = re.match(r'([a-z A-Z 0-9 \-]+)=([a-z A-Z 0-9 \-]+)', cond[i])
          	eq_cond = re.match(r'([a-z A-Z 0-9 \- \']+)=([a-z A-Z 0-9 \- \']+)', cond[i])
          	type_cond = re.match(r'type\(([a-z A-Z 0-9 \- \.]+)\)=([a-z A-Z 0-9 \- \.]+)',cond[i])
          	if (all_cond):
          		all_args_temp = re.findall(r'([a-z A-Z 0-9 \- \']+)', cond[i][6+len(all_cond.group(1)):])
          		all_args = []
          		for arg in all_args_temp:
					all_args.append(arg.replace(' ', ''))
          		all_args.append(all_cond.group(1))
          		cond_parsed[index].append(('all', 
          			all_args))
          	if (eq_cond):
          		cond_parsed[index].append(('equal',
          			[eq_cond.group(1), eq_cond.group(2)]))
          	if (type_cond):
          		cond_parsed[index].append(('type',
          			[type_cond.group(1), type_cond.group(2)]))                

	if debug: print "\tConditions: ", cond_parsed

	return cond_parsed

def main():
    output = open("facility_domain2.py", 'w')
    
    with open('causes.csv', 'rb') as f:
        reader = csv.reader(f)
        
        temp = []
        for row in reader:
            temp.append(row)

        # ignore first Header row
        causes_temp = temp[1:]

        # causes dictionary stores actions and intentions
        #	- intention is key, list of actions are values
        #	- actions are stored as tuples of (name, args list)
        causes  = {}
        longest_seq = 0;
        for cause in causes_temp:
            cause = filter(None, cause)
            ind = cause.index('causes')
            intention = cause[ind-1]
            actions_unparsed = cause[ind+1:]
            actions = []
            cond_index = len(actions_unparsed)
            cond_parsed = []
            if (actions_unparsed.count('if') == 1):
            	cond_index = actions_unparsed.index('if')
            	cond = actions_unparsed[cond_index+1:]
            	cond_parsed = parse_cond(cond)
	        actions_unparsed = actions_unparsed[:cond_index]
            for i in range(0, len(actions_unparsed)):
            	acts = actions_unparsed[i]
            	actions.append(parse_action(acts))
            acts_cond = actions, cond_parsed
            if (len(actions) > longest_seq):
                longest_seq = len(actions)
            if causes.has_key(intention):
                causes[intention].append(acts_cond)
            else:
                causes[intention] = [acts_cond]

        print "Causes: ",causes 
        
        prog = header + createPythonScript(causes, longest_seq) + footer

        output.write(prog)

def createPythonScript(causes, M):
    prog = ""
    for intention in causes:
        for result in causes[intention]:
            acts = "("
            for action in result[0]:
                acts += "\'"+action[0]+"\',"
            acts += ")"
            prog += "\tif actions == " + acts + ":\n"
            intention_parsed = parse_action(intention)
            intention_name = intention_parsed[0]
            intention_args = intention_parsed[1]
            if_stmt = '\t\tif '
            num_cond = 0
            for cond_set in result[1]:
            	for cond in cond_set:
            		if num_cond > 0:
            			if_stmt += ' and '
            		if cond[0] == 'type':
            			arg1 = cond[1][0]
            			i,j = get_cond_arg_indices(arg1, result[0])
            			arg2 = cond[1][1]
            			prog += '\t\tobject_id = arguments['+i+']['+j+']\n'
            			prog += '\t\tobject_type = lookup_type(object_id, states[0])\n'
            			if_stmt += 'object_type == \''+arg2+'\''
            		if cond[0] == 'equal':
            			arg1 = cond[1][0]
            			i1,j1 = get_cond_arg_indices(arg1, result[0])            			
            			arg2 = cond[1][1]
            			if (arg2[0] == '\''):
            				if_stmt += 'argument['+i1+']['+j1+'] == '+arg2
            			else:
            				i2,j2 = get_cond_arg_indices(arg2, result[0])            			
            				if_stmt += 'argument['+i1+']['+j1+'] == argument['+i2+']['+j2+']'
            		if cond[0] == 'all':
            			arg1 = cond[1][len(cond[1])-1]
            			arg2 = cond[1][:len(cond[1])-1]
            			arg_inds = ''
            			print "RESULT: ", result[0]
            			for arg in arg2:
            				if (arg[:4] == 'CONT'):
	            				i,j = get_cond_arg_indices(arg, result[0])            		
            					arg_inds += 'arguments['+i+']['+j+':]+'            		
            				else:
	            				i,j = get_cond_arg_indices(arg, result[0])            		            		
            					arg_inds += 'arguments['+i+']['+j+']+'
            				print "\tARGUMENT: ", arg, " (", i, ",", j, ")"            	            	       		
            			arg_inds = arg_inds[:len(arg_inds)-1]
            			prog += '\t\tall_'+arg1+' = [obj_id for (obj_id, obj_type,_,_,_,_) in states[0] if obj_type == \''+arg1+'\']\n'
            			if_stmt += 'set(all_'+arg1+') == set('+arg_inds+')'
            		num_cond += 1
            if (len(result[1]) > 0): 
            	if_stmt += ':\n\t'
            	prog += if_stmt
            # TODO: args plus doesn't work b/c not all strings
            #	- idea: have a function fold that creates list of args
            args = ''
            print "RESULT: ", result[0]
            for arg in intention_args:
            	if (arg[:4] == 'CONT'):
	            	i,j = get_cond_arg_indices(arg, result[0])            		
            		args += 'arguments['+i+']['+j+':]+'            		
            	else:
	            	i,j = get_cond_arg_indices(arg, result[0])            		            		
            		args += 'arguments['+i+']['+j+']+'
            	print "\tARGUMENT: ", arg, " (", i, ",", j, ")"            	            	
            args = args[:len(args)-1]
            prog += '\t\tg.add((states[0],\''+intention_name+'\','+args+'))\n'
    prog += "\treturn g\n"
    prog += "\nM="+str(M)+"\n\n"
    return prog

header = (
    'import sys\n'
    'sys.path.append(\'./copct-master\')\n'
    'import copct\n'
    'from load_facility_demo import load_demo\n'
    '\n'
    'def lookup_type(object_id, state):\n'
    '\treturn [obj_type for (obj_id,obj_type,_,_,_,_) in state if obj_id == object_id][0]\n'
    '\n'
    'def causes(v):\n'
    '\tstates, actions, arguments = zip(*v)\n'
    '\tg = set()\n'
)

footer = (
    'if __name__==\'__main__\':\n'
    '\n'
    '\t# Load demo\n'
    '\tdemo = load_demo(demo_directory=\'./SMILE-1.1.0/room_demo/\')\n'
    '\n'
    '\t# interpret demo (fixed-parameter-tractable when M is small and explicitly provided)\n'
    '\tstatus, tlcovs, g = copct.explain(causes, demo, M=M)\n'
    '\tprint(\'copct status: %s\'%status)\n'
    '\tprint(\'%d covers\'%len(tlcovs))\n'
    '\n'
    '\t# get most parsimonious covers\n'
    '\tpcovs, length = copct.minCardinalityTLCovers(tlcovs)\n'
    '\tprint(\'%d covers of length %d\'%(len(pcovs), length))\n'
    '\n'
    '\t# Show the first one\n'
    '\tprint(\'First cover of length %d:\'%length)\n'    
    '\tfor intention in pcovs[0][0]:\n'
    '\t\tprint(intention[1:])\n'
)

if __name__ == '__main__':
   main();
