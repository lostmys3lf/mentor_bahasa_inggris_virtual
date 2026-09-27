import src.core.env as env
import src.core.llm as llm
import src.agents.services as services
import src.core.prompts as prompts
import src.core.artifacts as artifacts

from src.repository.chat_repository import ChatRepository
# ini kenapa pake from dulu bukna import karena kita cuman mau make salah satu classnya aja

from google.genai import types


class LeadAgent:
    def __init__(self):
        # gemini
        self.gemini_client = llm.get_gemini_client()

        # agents
        self.tools = [
            services.skill_type_classification,
            services.evaluate_writing,
            services.get_learning_tip,
            services.evaluate_speaking,
        ]

        # chat repository
        self.chat_repository = ChatRepository()

        # lead agent instructions
        self.lead_agent_instructions = prompts.load_instruction("agent-lead")

    # pythonic way: atau ini function yang akan dipanggil secara private
    def _load_history(self, user_id: int):
        """Mengambil history chat dari supabase kemudian diubah ke format gemini"""
        response = self.chat_repository.load_history_by_user_id(user_id=user_id)

        # list comprehension
        return [
            types.Content(
                role=row["role"],
                parts=[types.Part(text=row["message_text"])],
            )
            for row in response.data
        ]

    def handle_send_message(self, user_id: int, message_text: str):
        """Menyimpan pesan user ke supabase dan mengirimkan ke gemini untuk mendapatkan balasan"""
        self.chat_repository.save_message(
            user_id=user_id, role="user", message_text=message_text
        )
        contents = self._load_history(user_id=user_id)

        # siapkan keranjang artifact untuk setiap request
        artifacts.start()

        def generate_report(username: str, start_date: str, end_date: str) -> str:
            """Membuat laporan belajar dari riwayat percakapan peserta saat ini."""
            path = services.generate_report(
                conversation_history=contents,
                username=username,
                start_date=start_date,
                end_date=end_date,
            )
            artifacts.add(path=path, kind="document", caption="Laporan belajar")
            return path

        response = self.gemini_client.models.generate_content(
            model=env.GEMINI_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=self.lead_agent_instructions,
                tools=[*self.tools, generate_report],
            ),
            contents=contents,
        )

        answer = response.text
        artifacts_data = artifacts.collect()
        # handle artifacts
        for item in artifacts_data:
            self.chat_repository.save_artifact(
                user_id=user_id, artifact_path=item["path"]
            )

        self.chat_repository.save_message(
            role="model", user_id=user_id, message_text=answer
        )

        return {
            "text": answer,
            "artifacts": artifacts_data,
        }

    def handle_send_voice(self, user_id: int, voice_file_path: str):
        self.chat_repository.save_message(
            user_id=user_id,
            role="user",
            message_text="[voice_note]",
        )
        evaluation_speaking_result = services.evaluate_speaking(voice_file_path)

        self.chat_repository.save_message(
            user_id=user_id,
            role="model",
            message_text=evaluation_speaking_result,
        )

        return evaluation_speaking_result

    def handle_report(
        self, user_id: int, username: str, start_date: str, end_date: str
    ):
        self.chat_repository.save_message(
            user_id=user_id,
            role="user",
            message_text=f"[generate learning report: {start_date} - {end_date}]",
        )

        history = self._load_history(user_id=user_id)
        report_file_path = services.generate_report(
            conversation_history=history,
            start_date=start_date,
            end_date=end_date,
            username=username,
        )

        self.chat_repository.save_message(
            user_id=user_id,
            role="model",
            message_text=f"[generate learning report: {start_date} - {end_date}] sudah selesai dicetak",
        )
        return report_file_path
