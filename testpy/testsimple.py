from durable.lang import *
import datetime

with ruleset('a1'):
    @when((m.subject == 'approve') & (m.amount > 1000))
    def denied(s):
        print ('a1 denied from: {0}'.format(s.id))
        s.status = 'done'
    
    @when((m.subject == 'approve') & (m.amount <= 1000))
    def request(s):
        print ('a1 request approval from: {0}'.format(s.id))
        s.status = 'pending'

    @when_all(m.subject == 'approved', s.status == 'pending')
    def second_request(s):
        print ('a1 second request approval from: {0}'.format(s.id))
        s.status = 'approved'

    @when(s.status == 'approved')
    def approved(s):
        print ('a1 approved from: {0}'.format(s.id))
        s.status = 'done'

    @when(m.subject == 'denied')
    def denied(s):
        print ('a1 denied from: {0}'.format(s.id))
        s.status = 'done'

    @when_start
    def start(host):
        host.post('a1', {'id': 1, 'sid': 1, 'subject': 'approve', 'amount': 100})
        host.post('a1', {'id': 2, 'sid': 1, 'subject': 'approved'})
        host.post('a1', {'id': 3, 'sid': 2, 'subject': 'approve', 'amount': 100})
        host.post('a1', {'id': 4, 'sid': 2, 'subject': 'denied'})
        host.post('a1', {'id': 5, 'sid': 3, 'subject': 'approve', 'amount': 10000})


with statechart('a2'):
    with state('input'):
        @to('denied')
        @when((m.subject == 'approve') & (m.amount > 1000))
        def denied(s):
            print ('a2 denied from: {0}'.format(s.id))
        
        @to('pending')    
        @when((m.subject == 'approve') & (m.amount <= 1000))
        def request(s):
            print ('a2 request approval from: {0}'.format(s.id))
        
    with state('pending'):
        @to('pending')
        @when(m.subject == 'approved')
        def second_request(s):
            print ('a2 second request approval from: {0}'.format(s.id))
            s.status = 'approved'

        @to('approved')
        @when(s.status == 'approved')
        def approved(s):
            print ('a2 approved from: {0}'.format(s.id))
        
        @to('denied')
        @when(m.subject == 'denied')
        def denied(s):
            print ('a2 denied from: {0}'.format(s.id))
        
    state('denied')
    state('approved')
    @when_start
    def start(host):
        host.post('a2', {'id': 1, 'sid': 1, 'subject': 'approve', 'amount': 100})
        host.post('a2', {'id': 2, 'sid': 1, 'subject': 'approved'})
        host.post('a2', {'id': 3, 'sid': 2, 'subject': 'approve', 'amount': 100})
        host.post('a2', {'id': 4, 'sid': 2, 'subject': 'denied'})
        host.post('a2', {'id': 5, 'sid': 3, 'subject': 'approve', 'amount': 10000})


with flowchart('a3'):
    with stage('input'): 
        to('request').when((m.subject == 'approve') & (m.amount <= 1000))
        to('deny').when((m.subject == 'approve') & (m.amount > 1000))
    
    with stage('request'):
        @run
        def request(s):
            print ('a3 request approval from: {0}'.format(s.id))
            if s.status:
                s.status = 'approved'
            else:
                s.status = 'pending'

        to('approve').when(s.status == 'approved')
        to('deny').when(m.subject == 'denied')
        to('request').when_any(m.subject == 'approved', m.subject == 'ok')
    
    with stage('approve'):
        @run 
        def approved(s):
            print ('a3 approved from: {0}'.format(s.id))

    with stage('deny'):
        @run
        def denied(s):
            print ('a3 denied from: {0}'.format(s.id))

    @when_start
    def start(host):
        host.post('a3', {'id': 1, 'sid': 1, 'subject': 'approve', 'amount': 100})
        host.post('a3', {'id': 2, 'sid': 1, 'subject': 'approved'})
        host.post('a3', {'id': 3, 'sid': 2, 'subject': 'approve', 'amount': 100})
        host.post('a3', {'id': 4, 'sid': 2, 'subject': 'denied'})
        host.post('a3', {'id': 5, 'sid': 3, 'subject': 'approve', 'amount': 10000})


with ruleset('p1'):
    with when(m.start == 'yes'): 
        with ruleset('one'):
            @when(-s.start)
            def continue_flow(s):
                s.start = 1

            @when(s.start == 1)
            def finish_one(s):
                print('p1 finish one {0}'.format(s.id))
                s.signal({'id': 1, 'end': 'one'})
                s.start = 2

        with ruleset('two'): 
            @when(-s.start)
            def continue_flow(s):
                s.start = 1

            @when(s.start == 1)
            def finish_two(s):
                print('p1 finish two {0}'.format(s.id))
                s.signal({'id': 1, 'end': 'two'})
                s.start = 2

    @when_all(m.end == 'one', m.end == 'two')
    def done(s):
        print('p1 done {0}'.format(s.id))

    @when_start
    def start(host):
        host.post('p1', {'id': 1, 'sid': 1, 'start': 'yes'})


with statechart('p2'):
    with state('input'):
        @to('process')
        @when(m.subject == 'approve')
        def get_input(s):
            print('p2 input {0} from: {1}'.format(s.event['quantity'], s.id))
            s.quantity = s.event['quantity']

    with state('process'):
        with to('result').when(+s.quantity):
            with statechart('first'):
                with state('evaluate'):
                    @to('end')
                    @when(s.quantity <= 5)
                    def signal_approved(s):
                        print('p2 signaling approved from: {0}'.format(s.id))
                        s.signal({'id': 1, 'subject': 'approved'})

                state('end')
        
            with statechart('second'):
                with state('evaluate'):
                    @to('end')
                    @when(s.quantity > 5)
                    def signal_denied(s):
                        print('p2 signaling denied from: {0}'.format(s.id))
                        s.signal({'id': 1, 'subject': 'denied'})
                
                state('end')
    
    with state('result'):
        @to('approved')
        @when(m.subject == 'approved')
        def report_approved(s):
            print('p2 approved from: {0}'.format(s.id))

        @to('denied')
        @when(m.subject == 'denied')
        def report_denied(s):
            print('p2 denied from: {0}'.format(s.id)) 
    
    state('denied')
    state('approved')

    @when_start
    def start(host):
        host.post('p2', {'id': 1, 'sid': 1, 'subject': 'approve', 'quantity': 3})
        host.post('p2', {'id': 2, 'sid': 2, 'subject': 'approve', 'quantity': 10})

with flowchart('p3'):
    with stage('start'):
        to('input').when(m.subject == 'approve')
    
    with stage('input'):
        @run
        def get_input(s):
            print('p3 input {0} from: {1}'.format(s.event['quantity'], s.id))
            s.quantity = s.event['quantity']

        to('process')
    
    with stage('process'):
        with flowchart('first'):
            with stage('start'):
                to('end').when(s.quantity <= 5)
            
            with stage('end'):
                @run
                def signal_approved(s):
                    print('p3 signaling approved from: {0}'.format(s.id))
                    s.signal({'id': 1, 'subject': 'approved'})

        with flowchart('second'):
            with stage('start'):
                to('end').when(s.quantity > 5)

            with stage('end'):
                @run
                def signal_denied(s):
                    print('p3 signaling denied from: {0}'.format(s.id))
                    s.signal({'id': 1, 'subject': 'denied'})

        to('approve').when(m.subject == 'approved')
        to('deny').when(m.subject == 'denied')

    with stage('approve'):
        @run
        def report_approved(s):
            print('p3 approved from: {0}'.format(s.id))

    with stage('deny'):
        @run
        def report_denied(s):
            print('p3 denied from: {0}'.format(s.id)) 

    @when_start
    def start(host):
        host.post('p3', {'id': 1, 'sid': 1, 'subject': 'approve', 'quantity': 3})
        host.post('p3', {'id': 2, 'sid': 2, 'subject': 'approve', 'quantity': 10})

with ruleset('t1'): 
    @when(m.start == 'yes')
    def start_timer(s):
        s.start = datetime.datetime.now().strftime('%I:%M:%S%p')
        s.start_timer('my_timer', 5)

    @when(timeout('my_timer'))
    def end_timer(s):
        print('t1 started @%s' % s.start)
        print('t1 ended @%s' % datetime.datetime.now().strftime('%I:%M:%S%p'))

    @when_start
    def start(host):
        host.post('t1', {'id': 1, 'sid': 1, 'start': 'yes'})


with statechart('t2'):
    with state('input'):
        with to('pending').when(m.subject == 'approve'):
            with statechart('first'):
                with state('send'):
                    @to('evaluate')
                    def start_timer(s):
                        s.start = datetime.datetime.now().strftime('%I:%M:%S%p')
                        s.start_timer('first', 4)   

                with state('evaluate'):
                    @to('end')
                    @when(timeout('first'))
                    def signal_approved(s):
                        s.signal({'id': 2, 'subject': 'approved', 'start': s.start})

                state('end')

            with statechart('second'):
                with state('send'):
                    @to('evaluate')
                    def start_timer(s):
                        s.start = datetime.datetime.now().strftime('%I:%M:%S%p')
                        s.start_timer('second', 3)

                with state('evaluate'):
                    @to('end')
                    @when(timeout('second'))
                    def signal_denied(s):
                        s.signal({'id': 3, 'subject': 'denied', 'start': s.start})

                state('end')

    with state('pending'):
        @to('approved')
        @when(m.subject == 'approved')
        def report_approved(s):
            print('t2 approved {0}'.format(s.id))
            print('t2 started @%s' % s.event['start'])
            print('t2 ended @%s' % datetime.datetime.now().strftime('%I:%M:%S%p'))

        @to('denied')
        @when(m.subject == 'denied')
        def report_denied(s):
            print('t2 denied {0}'.format(s.id))
            print('t2 started @%s' % s.event['start'])
            print('t2 ended @%s' % datetime.datetime.now().strftime('%I:%M:%S%p'))

    state('approved')
    state('denied')
    
    @when_start
    def start(host):
        host.post('t2', {'id': 1, 'sid': 1, 'subject': 'approve'})

run_all()