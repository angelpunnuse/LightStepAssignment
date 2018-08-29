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
                                            default='BubbleSortComponent')
    args = parser.parse_args()

    return lightstep.Tracer(
            component_name=args.component_name,
            access_token=args.token,
            collector_host=args.host,
            collector_port=args.port,
            verbosity=1,
            collector_encryption=('tls' if args.use_tls else 'none'))


def bubble_sort(array,parent_span):
    with opentracing.start_child_span(parent_span, operation_name='bubbleSort/bubbleSortExecution') as child_span:
            child_span.log_event('Executing bubbleSort', payload={'array': array})
            child_span.set_tag('span_type', 'child')
            for i in range(len(array)):
                for j in range(i+1, len(array)):
                    if len(array[j]) < len(array[i]):
                        time.sleep(0.05)
                        array[j], array[i] = array[i], array[j]
                        payLoadMessage = '({},{}) => swapped => ({},{})'.format( array[j], array[i], array[i], array[j] )
                        print(payLoadMessage)
                        child_span.log_event('Swapping elements', payload={'swapped':payLoadMessage })
    opentracing.tracer.flush()
    return array

def doTheSort():
    with opentracing.tracer.start_span(operation_name='bubbleSort/apiCall') as span:
        span.set_tag(   'span_type', 'parent')
        dataset = ['engineering', 'trace', 'microservices', 'span', 'lightstep', 'histogram', 'tag']
        span.log_event( 'Starting the bubble sort', payload={ 'dataset' : ['engineering', 'trace', 'microservices', 'span', 'lightstep', 'histogram', 'tag'] })

        print("Unsorted dataset: " + str(dataset))
        sorted = bubble_sort(dataset,span)
        print("Sorted dataset: " + str(sorted))

        span.log_event('Finished the bubble sort', payload={'sorted': sorted})

if __name__ == '__main__':
    with lightstep_tracer_from_args() as tracer:
        opentracing.tracer = tracer
        doTheSort()

