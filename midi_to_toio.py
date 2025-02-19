import mido
import json
import os
from multiprocessing import Pool, cpu_count
from functools import partial

def midi_to_toio_notes(midi_file_path):
    # MIDIファイルの読み込み
    try:
        midi_file = mido.MidiFile(midi_file_path)
        print(f"Loaded MIDI file: {midi_file_path}")
    except Exception as e:
        print(f"Failed to load MIDI file: {midi_file_path}, Error: {e}")
        return

    # テンポの取得（デフォルトのテンポを設定）
    tempo = 500000  # デフォルトのテンポ（500,000マイクロ秒/拍 = 120BPM）
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = msg.tempo
                break
        else:
            continue
        break

    ticks_per_beat = midi_file.ticks_per_beat

    # 時間の変換用の係数
    tick_time = tempo / ticks_per_beat  # 1tickあたりの時間（マイクロ秒）
    # print(f"Tempo: {tempo} microseconds per beat")
    # print(f"Ticks per beat: {ticks_per_beat}")
    # print(f"Tick time: {tick_time} microseconds per tick")

    # 全トラックのデータを格納するリスト
    tracks_data = []
    priority_counter = 1  # 優先度のカウンターを初期化

    # トラックごとに処理
    for i, track in enumerate(midi_file.tracks):
        current_time = 0  # 累積時間（ticks）
        note_on_events = {}

        # print(f"Processing Track {i}: {track.name}")

        track_notes = []

        # トラック名を取得（なければ番号）
        track_name = track.name if track.name else f"Track {i}"

        for msg in track:
            current_time += msg.time  # 時間を累積

            if msg.type == 'set_tempo':
                # 曲中でテンポが変更された場合に対応
                tempo = msg.tempo
                tick_time = tempo / ticks_per_beat  # 1tickあたりの時間（マイクロ秒）
                # print(f"Tempo change detected at {current_time} ticks: {tempo} microseconds per beat")
                continue

            if msg.type == 'note_on' and msg.velocity > 0:
                # Note On イベント
                note_on_events.setdefault(msg.note, []).append(current_time)
            elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                # Note Off イベント
                if msg.note in note_on_events and note_on_events[msg.note]:
                    start_time = note_on_events[msg.note].pop(0)
                    duration = current_time - start_time

                    # 時間をミリ秒に変換
                    start_time_ms = (start_time * tick_time) / 1000  # ミリ秒
                    duration_ms = (duration * tick_time) / 1000  # ミリ秒

                    note_number = msg.note

                    # toioの音程範囲（45～81）に合わせて音程を調整
                    original_note_number = note_number  # デバッグ用
                    while note_number < 45:
                        note_number += 12
                    while note_number > 81:
                        note_number -= 12

                    # 再生時間を10ms単位に変換（1～255の範囲）
                    play_time_units = int(duration_ms / 10)
                    if play_time_units < 1:
                        play_time_units = 1
                    elif play_time_units > 255:
                        play_time_units = 255

                    # 音符情報を保存
                    note_info = {
                        'note_number': note_number,
                        'start_time_ms': int(start_time_ms),
                        'duration_units': play_time_units
                    }
                    track_notes.append(note_info)

                    # デバッグ用の出力をコメントアウトまたは削除可能
                    # print(f"{track_name}, Note {original_note_number} ({start_time_ms:.2f} ms): Duration {duration_ms:.2f} ms, Adjusted Note {note_number}, Play Time Units {play_time_units}")

        if track_notes:
            # トラック情報を保存
            track_data = {
                'track_name': track_name,
                'priority': priority_counter,
                'notes': track_notes
            }
            tracks_data.append(track_data)
            priority_counter += 1  # 音符情報があるトラックに対してのみ優先度を増加

    if not tracks_data:
        print(f"No note data found in MIDI file: {midi_file_path}")
        return

    # 各トラックの音符を開始時間でソート
    for track_data in tracks_data:
        track_data['notes'].sort(key=lambda x: x['start_time_ms'])

    # MIDIファイル名からJSONファイル名を生成
    midi_filename = os.path.basename(midi_file_path)
    midi_name, _ = os.path.splitext(midi_filename)
    output_json_filename = f'{midi_name}_processed.json'
    output_json_path = os.path.join(os.path.dirname(midi_file_path), output_json_filename)

    # データをJSONファイルに保存
    try:
        with open(output_json_path, 'w') as f:
            json.dump(tracks_data, f, indent=2)
            print(f"Notes have been saved to {output_json_path}")
    except Exception as e:
        print(f"Failed to save JSON file: {output_json_path}, Error: {e}")

def collect_midi_files(root_dir):
    midi_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.lower().endswith(('.mid', '.midi')):
                midi_file_path = os.path.join(dirpath, filename)
                midi_files.append(midi_file_path)
    return midi_files

def process_all_midis(root_dir):
    midi_files = collect_midi_files(root_dir)
    total_files = len(midi_files)
    print(f"Total MIDI files to process: {total_files}")

    cpu_cores = cpu_count()
    print(f"Using {cpu_cores} CPU cores for parallel processing")

    with Pool(processes=cpu_cores) as pool:
        pool.map(midi_to_toio_notes, midi_files)

if __name__ == '__main__':
    import sys

    # dataディレクトリのパスを指定
    data_dir = 'data'  # スクリプトの実行ディレクトリに対する相対パス

    # コマンドライン引数でデータディレクトリを指定可能
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]

    if not os.path.exists(data_dir):
        print(f"The specified directory does not exist: {data_dir}")
        sys.exit(1)

    process_all_midis(data_dir)