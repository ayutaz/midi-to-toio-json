import pygame
import sys

def play_midi(midi_file):
    # pygameを初期化
    pygame.init()

    # MIDIミキサーを初期化
    pygame.mixer.init()

    # MIDIファイルをロード
    try:
        pygame.mixer.music.load(midi_file)
        print(f"MIDIファイル '{midi_file}' をロードしました。")
    except pygame.error as e:
        print(f"MIDIファイル '{midi_file}' のロードに失敗しました: {e}")
        sys.exit(1)

    # MIDIファイルを再生
    pygame.mixer.music.play()
    print("再生を開始しました。")

    # 再生が終了するまで待機
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    print("再生が終了しました。")
    pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python play_midi.py <MIDIファイルのパス>")
        sys.exit(1)

    midi_file_path = sys.argv[1]
    play_midi(midi_file_path)