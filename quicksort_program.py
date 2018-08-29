"""
Angel Punnuse - Lightstep Technical Account Manager Evaluation
"""
import argparse
import opentracing
import lightstep
import time

def lightstep_tracer_from_args():
    """Initializes lightstep from the commandline args.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--token',          help='Your LightStep access token.',
                                            default='e1986102935312341f341ab268e23678')
    parser.add_argument('--host',           help='The LightStep reporting service host to contact.',
                                            default='collector.lightstep.com')
    parser.add_argument('--port',           help='The LightStep reporting service port.',
                                            type=int, default=443)
    parser.add_argument('--use_tls',        help='Whether to use TLS for reporting',
                                            type=bool, default=True)
    parser.add_argument('--component_name', help='The LightStep component name',
                                            default='QuickSortComponent')
    args = parser.parse_args()

    return lightstep.Tracer(
            component_name=args.component_name,
            access_token=args.token,
            collector_host=args.host,
            collector_port=args.port,
            verbosity=1,
            collector_encryption=('tls' if args.use_tls else 'none'))

def quick_sorter(array, span, depth=0):

    #The code that figues what child+depth we are in the call stack
    operationName   = 'quickSort/execution'
    childName       = 'quick' + str(depth)
    with opentracing.start_child_span(span, operation_name=operationName) as child_span:
        child_span.log_event('Starting quickSort call...', payload={'childName' : childName , 'array': array } )
        child_span.set_tag('span_type', childName)

        less    = []
        equal   = []
        greater = []
        if len(array) > 1:
            pivot = len(array[0])
            for x in array:
                    if len(x) < pivot:
                        less.append(x)
                    if len(x) == pivot:
                        equal.append(x)
                    if len(x) > pivot:
                        greater.append(x)
            toReturn = quick_sorter( less, span=child_span, depth = depth+1 ) + equal + quick_sorter( greater, span=child_span, depth = depth+1 )
        else:
            toReturn = array
        child_span.log_event('Done quickSort call', payload={'childName': childName, 'array': array})
    time.sleep(0.05)
    opentracing.tracer.flush()

    return toReturn

def doTheSort():
    with opentracing.tracer.start_span(operation_name='quickSort/apiCall') as span:
        span.set_tag(   'span_type', 'parent')
        span.log_event( 'Starting the bubble sort', payload={ 'dataset' : ['engineering', 'trace', 'microservices', 'span', 'lightstep', 'histogram', 'tag'] })

    dataset = ['engineering', 'trace', 'microservices', 'span', 'lightstep', 'histogram', 'tag']
    print("Unsorted dataset: " + str(dataset))
    sorted = quick_sorter(dataset, span)
    print("Sorted dataset: " + str(sorted))

if __name__ == '__main__':
    with lightstep_tracer_from_args() as tracer:
        opentracing.tracer = tracer
        doTheSort()
