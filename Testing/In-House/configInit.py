import sys

config = dict()
ra = []


def init(param = None):
    global config
    global ra

    with open('config.txt','r') as configFile:
        for line in configFile:
            if not line == '\n':
                field = line.split(',')[0]
                data = line.split(',')[1].split('|')
                if len(data) > 1:
                    config.update( { field : ( data[0], data[1][:-1] ) } )
                else:
                    config.update( { field : data[0][:-1] } )


    ## Printing info dictionary for debugging
    # for key in config:
    #    print(key,':',config[key])
    
    if param is None:
        print('Usage:: [FILENAME].py [PARAM]')
        print('Param List...\n')
        print('kuilin\t->\tThis sets the following variables:')
        print('\t\tIP\t\t-> %s' % config['kuilin'] )
        print('\t\tCred.\t\t-> ( %s, %s )' % ( config['credentials'][0], config['credentials'][1] ) )
        print('\t\tRouting Key\t-> %s' % config['routing key_K'] )
        print('\t\tExchange\t-> %s\n' % config['exchange'] )
        
        print('beta\t->\tThis sets the following variables:')
        print('\t\tIP\t\t-> %s' % config['beta'] )
        print('\t\tCred.\t\t-> ( %s, %s )' % ( config['credentials'][0], config['credentials'][1] ) )
        print('\t\tRouting Key\t-> %s' % config['routing key_B'] )
        print('\t\tExchange\t-> %s\n' % config['exchange'] )

        print('sam\t->\tThis sets the following variables:')
        print('\t\tIP\t\t-> %s' % config['localhost'] )
        print('\t\tRouting Key\t-> %s' % config['routing key_S'] )
        print('\t\tExchange\t-> %s\n' % config['exchange'] )

        print('mobile_lab\t->\tThis sets the following variables:')
        print('\t\tIP\t\t-> %s' % config['mobile lab'] )
        print('\t\tCred.\t\t-> ( %s, %s )' % ( config['credentials'][0], config['credentials'][1] ) )
        print('\t\tRouting Key\t-> %s' % config['routing key_M'] )
        print('\t\tExchange\t-> %s\n' % config['exchange'] )

        print('tony_url\t->\tThis sets the following variables:')
        print('\t\tIP\t\t-> %s' % config['tony url'] )
        print('\t\tRouting Key\t-> %s' % config['routing key_T'] )
        print('\t\tExchange\t-> %s\n' % config['exchange'] )

        print('override\t->\tThis allows you to input your own information')
        print('\t\t\tConsider editing the file to contain custom information\n\n')

        try:
            usr = input('Press CTRL + C to exit\n').split(' ')
        except KeyboardInterrupt:
            exit()

        if len(usr) >= 1:
            init(usr[0])
        else:
            init()
            
    elif param.lower() == 'kuilin':
        ra = [config['kuilin'],config['credentials'],config['exchange'],config['routing key_K']]
    elif param.lower() == 'beta':
        ra = [config['beta'],config['credentials'],config['exchange'],config['routing key_B']]
    elif param.lower() == 'sam':
        ra = [config['localhost'],(None, None),config['exchange'],config['routing key_S']]
    elif param.lower() == 'mobile_lab':
        ra = [config['mobile lab'],config['credentials'],config['exchange'],config['routing key_M']]
    elif param.lower() == 'tony_url':
        ra = [config['tony url'],config['exchange'],config['routing key_T']]
    elif param.lower() == 'override' or param.lower() == 'ov':
        print('Press ENTER to skip any of the following fields.\n')
        
        ip = input('What IP are you connecting to?\t')
        if not len(ip) == 0:
            ra.append(ip)
        else:
            ra.append(None)
            
        usr = input('Username?\t\t\t')
        pas = input('Password?\t\t\t')
        if len(usr) is 0 or len(pas) is 0:
            ra.append( ( None, None ) )
        else:
            ra.append( ( usr, pas ) )
            
        xch = input('Through what exchange?\t\t')
        if not len(xch) == 0:
            ra.append(xch)
        else:
            ra.append(None)
            
        rtk = input('With what routing key?\t\t')
        if not len(rtk) == 0:
            ra.append(rtk)
        else:
            ra.append(None)

        print('\n')

    else:
        init()
        
    #print(ra)
    return ra
        


## Testing
##if len(sys.argv) > 1:
##    init(str(sys.argv[1]))
##else:
##    init()


