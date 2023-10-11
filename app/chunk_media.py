from pydub import AudioSegment

def chunk_audio_file(audio_file_path, chunk_size_in_minutes=10):
    audio_extension = audio_file_path.split('.')[-1]
    audio_file = AudioSegment.from_mp3( audio_file_path )
    output_prefix = '{}_chunk_'.format( audio_file_path.split('.')[0] )

    # PyDub handles time in milliseconds
    one_second = 1000
    one_minute = one_second * 60
    segment_size = one_minute * chunk_size_in_minutes

    total_duration_seconds = round(audio_file.duration_seconds + 1)
    total_duration_ms = total_duration_seconds * 1000

    print ('Total duration[ms]:{}'.format( total_duration_ms))

    chunk_unit = segment_size
    chunked_file_names = []
    for indx, audio_segment in enumerate(range(0, total_duration_ms, chunk_unit)):
        start = audio_segment
        end = min(audio_segment+chunk_unit, total_duration_ms)

        chunk_file_name = output_prefix + str(indx+1) + '.' + audio_extension
        chunked_file_names.append( chunk_file_name )
        print ('indx:{}, from[ms]:{} to[ms]:{}'.format( indx, start, end))
        audio_file[start:end].export(chunk_file_name, format=audio_extension)

    return chunked_file_names


def main():
    chunk_audio_file()

if __name__ == "__main__":
    main()
