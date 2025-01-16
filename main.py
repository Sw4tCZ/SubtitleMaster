import tkinter as tk
from tkinter import filedialog, messagebox
from moviepy.video.io.VideoFileClip import VideoFileClip
from faster_whisper import WhisperModel
from datetime import timedelta
import os

class SubtitleMasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SubtitleMaster")
        
        # Hlavní obrazovka
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(pady=20)
        
        self.upload_button = tk.Button(self.main_frame, text="Nahrát video", command=self.upload_video)
        self.upload_button.pack(pady=10)
        
        self.video_listbox = tk.Listbox(self.main_frame, width=50)
        self.video_listbox.pack(pady=10)
        
        self.process_button = tk.Button(self.main_frame, text="Zpracovat video", command=self.process_video)
        self.process_button.pack(pady=10)
        
        self.settings_button = tk.Button(self.main_frame, text="Nastavení", command=self.show_settings)
        self.settings_button.pack(pady=10)
        
        # Obrazovka pro zpracování videa
        self.process_frame = tk.Frame(root)
        
        self.video_label = tk.Label(self.process_frame, text="Náhled videa")
        self.video_label.pack(pady=10)
        
        self.extract_audio_button = tk.Button(self.process_frame, text="Extrahovat audio", command=self.extract_audio)
        self.extract_audio_button.pack(pady=10)
        
        self.generate_subtitles_button = tk.Button(self.process_frame, text="Generovat titulky", command=self.generate_subtitles)
        self.generate_subtitles_button.pack(pady=10)

        self.back_button_process = tk.Button(self.process_frame, text="Zpět", command=self.show_main)
        self.back_button_process.pack(pady=10)
        
        self.progress_label = tk.Label(self.process_frame, text="")
        self.progress_label.pack(pady=10)
        
        
        # Obrazovka s výsledky
        self.results_frame = tk.Frame(root)
        
        self.results_label = tk.Label(self.results_frame, text="Náhled videa s titulky")
        self.results_label.pack(pady=10)
        
        self.download_subtitles_button = tk.Button(self.results_frame, text="Stáhnout titulky", command=self.download_subtitles)
        self.download_subtitles_button.pack(pady=10)

        self.back_button_results = tk.Button(self.results_frame, text="Zpět", command=self.show_main)
        self.back_button_results.pack(pady=10)
        
        # Nastavení
        self.settings_frame = tk.Frame(root)
        
        self.model_label = tk.Label(self.settings_frame, text="Výběr modelu")
        self.model_label.pack(pady=10)
        
        self.model_var = tk.StringVar(value="large-v2")
        self.model_options = ["base", "small", "medium", "large-v2"]
        self.model_menu = tk.OptionMenu(self.settings_frame, self.model_var, *self.model_options)
        self.model_menu.pack(pady=10)

        # Přidání výběru jazyka aplikace
        self.app_language_label = tk.Label(self.settings_frame, text="Jazyk aplikace")
        self.app_language_label.pack(pady=10)

        self.app_language_var = tk.StringVar(value="cs")
        self.app_language_options = ["cs", "en", "de", "fr", "es", "it", "pt", "ru", "zh", "ja"]  # Přidejte další jazyky podle potřeby
        self.app_language_menu = tk.OptionMenu(self.settings_frame, self.app_language_var, *self.app_language_options, command=self.change_language)
        self.app_language_menu.pack(pady=10)

        # Jazykové nastavení pro transkripci (automatické rozpoznání jazyka audia)
        self.language_var = tk.StringVar(value="auto")

        self.back_button = tk.Button(self.settings_frame, text="Zpět", command=self.show_main)
        self.back_button.pack(pady=10)

    def upload_video(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.video_listbox.insert(tk.END, file_path)

    def process_video(self):
        selected_video_index = self.video_listbox.curselection()
        if not selected_video_index:
            messagebox.showwarning("Varování", "Vyberte video k zpracování.")
            return
        
        video_path = self.video_listbox.get(selected_video_index)
        
        # Přepnutí na obrazovku pro zpracování videa
        self.main_frame.pack_forget()
        self.process_frame.pack(pady=20)

    def extract_audio(self):
        selected_video_index = self.video_listbox.curselection()
        video_path = self.video_listbox.get(selected_video_index)

        video = VideoFileClip(video_path)
        audio_output_path = "extracted_audio.wav"
    
        try:
            video.audio.write_audiofile(audio_output_path)
            messagebox.showinfo("Úspěch", "Audio bylo úspěšně extrahováno.")
            # Aktivace tlačítka Generovat titulky po úspěšné extrakci audia
            self.generate_subtitles_button.config(state=tk.NORMAL)
        
            # Uložení cesty k extrahovanému audio souboru
            self.audio_output_path = audio_output_path
        
        except Exception as e:
            messagebox.showerror("Chyba", f"Audio nebylo extrahováno: {e}")
            return

    def generate_subtitles(self):
        if not hasattr(self, 'audio_output_path') or not os.path.exists(self.audio_output_path):
            messagebox.showerror("Chyba", "Audio není k dispozici.")
            return
    
        audio_output_path = self.audio_output_path
    
        model_size = self.model_var.get()
    
        model = WhisperModel(model_size, device="cpu")
    
        segments, info = model.transcribe(audio_output_path)

        subtitles_content = self.convert_to_srt(segments)

        subtitles_path = "subtitles.srt"
        with open(subtitles_path, "w", encoding="utf-8") as f:
            f.write(subtitles_content)

        self.progress_label.config(text="Titulky byly úspěšně vygenerovány.")

    def download_subtitles(self):
        subtitles_path = "subtitles.srt"
        filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("SRT files", "*.srt")])

    def convert_to_srt(self, segments):
        srt_content = ""
        for i, segment in enumerate(segments, start=1):
            start_time = self.format_timestamp(segment.start)
            end_time = self.format_timestamp(segment.end)
            text = segment.text.strip()
            srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"
        return srt_content

    def format_timestamp(self, seconds):
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        milliseconds = int((td.total_seconds() - total_seconds) * 1000)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03d}"

    def show_settings(self):
        self.main_frame.pack_forget()
        self.settings_frame.pack(pady=20)

    def show_main(self):
        self.settings_frame.pack_forget()
        self.process_frame.pack_forget()
        self.results_frame.pack_forget()
        self.main_frame.pack(pady=20)

    def change_language(self, lang_code):
        translations = {
            "cs": {
                "upload_video": "Nahrát video",
                "process_video": "Zpracovat video",
                "settings": "Nastavení",
                "extract_audio": "Extrahovat audio",
                "generate_subtitles": "Generovat titulky",
                "download_subtitles": "Stáhnout titulky",
                "back": "Zpět",
                "app_language": "Jazyk aplikace",
                "model_selection": "Výběr modelu"
            },
            "en": {
                "upload_video": "Upload Video",
                "process_video": "Process Video",
                "settings": "Settings",
                "extract_audio": "Extract Audio",
                "generate_subtitles": "Generate Subtitles",
                "download_subtitles": "Download Subtitles",
                "back": "Back",
                "app_language": "App Language",
                "model_selection": "Model Selection"
            },
            "de": {
                "upload_video": "Video hochladen",
                "process_video": "Video verarbeiten",
                "settings": "Einstellungen",
                "extract_audio": "Audio extrahieren",
                "generate_subtitles": "Untertitel generieren",
                "download_subtitles": "Untertitel herunterladen",
                "back": "Zurück",
                "app_language": "App-Sprache",
                "model_selection": "Modellauswahl"
            },
            "fr": {
                "upload_video": "Télécharger la vidéo",
                "process_video": "Traiter la vidéo",
                "settings": "Paramètres",
                "extract_audio": "Extraire l'audio",
                "generate_subtitles": "Générer des sous-titres",
                "download_subtitles": "Télécharger les sous-titres",
                "back": "Retour",
                "app_language": "Langue de l'application",
                "model_selection": "Sélection du modèle"
            },
            "es": {
                "upload_video": "Subir video",
                "process_video": "Procesar video",
                "settings": "Configuraciones",
                "extract_audio": "Extraer audio",
                "generate_subtitles": "Generar subtítulos",
                "download_subtitles": "Descargar subtítulos",
                "back": "Atrás",
                "app_language": "Idioma de la aplicación",
                "model_selection": "Selección de modelo"
            },
            "it": {
                "upload_video": "Carica video",
                "process_video": "Elabora video",
                "settings": "Impostazioni",
                "extract_audio": "Estrai audio",
                "generate_subtitles": "Genera sottotitoli",
                "download_subtitles": "Scarica sottotitoli",
                "back": "Indietro",
                "app_language": "Lingua dell'app",
                "model_selection": "Selezione del modello"
            },
            "pt": {
                "upload_video": "Carregar vídeo",
                "process_video": "Processar vídeo",
                "settings": "Configurações",
                "extract_audio": "Extrair áudio",
                "generate_subtitles": "Gerar legendas",
                "download_subtitles": "Baixar legendas",
                "back": "Voltar",
                "app_language": "Idioma do aplicativo",
                "model_selection": "Seleção de modelo"
            },
            "ru": {
                "upload_video": "Загрузить видео",
                "process_video": "Обработать видео",
                "settings": "Настройки",
                "extract_audio": "Извлечь аудио",
                "generate_subtitles": "Создать субтитры",
                "download_subtitles": "Скачать субтитры",
                "back": "Назад",
                "app_language": "Язык приложения",
                "model_selection": "Выбор модели"
            },
            "zh": {
                "upload_video": "上传视频",
                "process_video": "处理视频",
                "settings": "设置",
                "extract_audio": "提取音频",
                "generate_subtitles": "生成字幕",
                "download_subtitles": "下载字幕",
                "back": "返回",
                "app_language": "应用语言",
                "model_selection": "模型选择"
            },
            "ja": {
                "upload_video": "ビデオをアップロード",
                "process_video": "ビデオを処理",
                "settings": "設定",
                "extract_audio": "オーディオを抽出",
                "generate_subtitles": "字幕を生成",
                "download_subtitles": "字幕をダウンロード",
                "back": "戻る",
                "app_language": "アプリ言語",
                "model_selection": "モデル選択"
            }

}

        self.upload_button.config(text=translations[lang_code]["upload_video"])
        self.process_button.config(text=translations[lang_code]["process_video"])
        self.settings_button.config(text=translations[lang_code]["settings"])
        self.extract_audio_button.config(text=translations[lang_code]["extract_audio"])
        self.generate_subtitles_button.config(text=translations[lang_code]["generate_subtitles"])
        self.download_subtitles_button.config(text=translations[lang_code]["download_subtitles"])
        self.back_button.config(text=translations[lang_code]["back"])
        self.app_language_label.config(text=translations[lang_code]["app_language"])
        self.model_label.config(text=translations[lang_code]["model_selection"])

if __name__ == "__main__":
    root = tk.Tk()
    app = SubtitleMasterApp(root)
    root.mainloop()
