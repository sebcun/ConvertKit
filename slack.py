# slack_bot.py
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
import uuid
import requests
from core.loader import load_plugins
from dotenv import load_dotenv

load_dotenv()

# Initialize Slack app
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# Load plugins
plugins = load_plugins()
print(f"Loaded Plugins for Slack Bot: {plugins}")

pending_conversions = {}


@app.view("file_upload_modal")
def handle_modal_submission(ack, body, client, view):
    ack()
    
    user_id = body["user"]["id"]
    channel_id = body["view"]["private_metadata"] if "private_metadata" in body["view"] else None
    
    file_input = view["state"]["values"]["file_input"]["file_upload"]
    
    if not file_input.get("files") or len(file_input["files"]) == 0:
        return
    
    file_id = file_input["files"][0]["id"]
    
    try:
        result = client.files_info(file=file_id)
        file_info = result["file"]
        
        filename = file_info["name"]
        ext = filename.split(".")[-1].lower()
        url_private = file_info["url_private_download"]
        
        compatible_plugins = [p for p in plugins if p["input"] == ext]
        
        channel_id = body.get("view", {}).get("private_metadata") or file_info.get("channels", [None])[0]
        
        if not compatible_plugins:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f"❌ No conversions available for `.{ext}` files."
            )
            return
        
        os.makedirs("uploads", exist_ok=True)
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join("uploads", unique_filename)
        
        headers = {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN')}"}
        response = requests.get(url_private, headers=headers)
        
        with open(file_path, "wb") as f:
            f.write(response.content)
        
        conversion_id = str(uuid.uuid4())
        pending_conversions[conversion_id] = {
            "file_path": file_path,
            "original_filename": filename,
            "channel_id": channel_id,
            "user_id": user_id
        }
        
        options = [
            {
                "text": {
                    "type": "plain_text",
                    "text": f"{plugin['name']} ({plugin['input']} → {plugin['output']})"
                },
                "value": f"{conversion_id}|{plugin['module'].__name__}"
            }
            for plugin in compatible_plugins
        ]
        
        client.chat_postEphemeral(
            channel=channel_id,
            user=user_id,
            text=f"📁 *{filename}* uploaded! Choose a conversion:",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{filename}* uploaded! Choose a conversion:"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select conversion..."
                            },
                            "options": options,
                            "action_id": "conversion_selected"
                        }
                    ]
                }
            ]
        )
        
    except Exception as e:
        print(f"Error handling file from modal: {e}")
        client.chat_postEphemeral(
            channel=channel_id or "general",
            user=user_id,
            text=f"❌ Error processing file: {str(e)}"
        )


@app.command("/convert")
def handle_convert_command(ack, command, client):
    ack()
    
    channel_id = command["channel_id"]
    
    try:
        client.views_open(
            trigger_id=command["trigger_id"],
            view={
                "type": "modal",
                "callback_id": "file_upload_modal",
                "private_metadata": channel_id,
                "title": {"type": "plain_text", "text": "Convert File"},
                "submit": {"type": "plain_text", "text": "Convert"},
                "close": {"type": "plain_text", "text": "Cancel"},
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Upload a file to convert:"
                        }
                    },
                    {
                        "type": "input",
                        "block_id": "file_input",
                        "element": {
                            "type": "file_input",
                            "action_id": "file_upload",
                            "filetypes": ["jpg", "jpeg", "png", "bmp", "webp", "pdf", "docx", "pptx", "txt"]
                        },
                        "label": {"type": "plain_text", "text": "Select a file"}
                    }
                ]
            }
        )
    except Exception as e:
        print(f"Error opening modal: {e}")
        client.chat_postEphemeral(
            channel=channel_id,
            user=command["user_id"],
            text=f"❌ Error opening file dialog: {str(e)}"
        )
                                                


@app.event("file_shared")
def handle_file_shared(event, client, say):
    file_id = event["file_id"]
    user_id = event["user_id"]
    channel_id = event.get("channel_id")
    
    try:
        result = client.files_info(file=file_id)
        file_info = result["file"]
        
        filename = file_info["name"]
        ext = filename.split(".")[-1].lower()
        url_private = file_info["url_private_download"]
        
        compatible_plugins = [p for p in plugins if p["input"] == ext]
        
        if not compatible_plugins:
            client.chat_postEphemeral(
                channel=channel_id or file_info.get("channels", [None])[0],
                user=user_id,
                text=f"❌ No conversions available for `.{ext}` files."
            )
            return
        
        os.makedirs("uploads", exist_ok=True)
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join("uploads", unique_filename)
        
        headers = {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN')}"}
        response = requests.get(url_private, headers=headers)
        
        with open(file_path, "wb") as f:
            f.write(response.content)
        
        conversion_id = str(uuid.uuid4())
        pending_conversions[conversion_id] = {
            "file_path": file_path,
            "original_filename": filename,
            "channel_id": channel_id or file_info.get("channels", [None])[0],
            "user_id": user_id
        }
        
        options = [
            {
                "text": {
                    "type": "plain_text",
                    "text": f"{plugin['name']} ({plugin['input']} → {plugin['output']})"
                },
                "value": f"{conversion_id}|{plugin['module'].__name__}"
            }
            for plugin in compatible_plugins
        ]
        
        client.chat_postEphemeral(
            channel=channel_id or file_info.get("channels", [None])[0],
            user=user_id,
            text=f"📁 *{filename}* uploaded! Choose a conversion:",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{filename}* uploaded! Choose a conversion:"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "static_select",
                            "placeholder": {
                                "type": "plain_text",
                                "text": "Select conversion..."
                            },
                            "options": options,
                            "action_id": "conversion_selected"
                        }
                    ]
                }
            ]
        )
        
    except Exception as e:
        print(f"Error handling file: {e}")
        if channel_id:
            client.chat_postEphemeral(
                channel=channel_id,
                user=user_id,
                text=f"❌ Error processing file: {str(e)}"
            )


@app.action("conversion_selected")
def handle_conversion_selection(ack, body, client):
    ack()
    
    selected_value = body["actions"][0]["selected_option"]["value"]
    conversion_id, module_name = selected_value.split("|")
    
    if conversion_id not in pending_conversions:
        client.chat_postEphemeral(
            channel=body["channel"]["id"],
            user=body["user"]["id"],
            text="❌ Conversion expired. Please upload the file again."
        )
        return
    
    file_info = pending_conversions[conversion_id]
    file_path = file_info["file_path"]
    original_filename = file_info["original_filename"]
    channel_id = file_info["channel_id"]
    
    plugin = next((p for p in plugins if p["module"].__name__ == module_name), None)
    
    if not plugin:
        client.chat_postEphemeral(
            channel=channel_id,
            user=body["user"]["id"],
            text="❌ Invalid plugin selected."
        )
        if os.path.exists(file_path):
            os.remove(file_path)
        del pending_conversions[conversion_id]
        return
    
    try:
        client.chat_postEphemeral(
            channel=channel_id,
            user=body["user"]["id"],
            text=f"⏳ Converting *{original_filename}*..."
        )
        
        output_file = plugin["module"].convert(file_path)
        
        name, ext_in = os.path.splitext(original_filename)
        ext_in = ext_in.lstrip(".")
        output_ext = plugin["output"]
        
        if output_ext == ext_in:
            attachment_filename = f"{name}_converted.{output_ext}"
        else:
            attachment_filename = f"{name}.{output_ext}"
        
        client.files_upload_v2(
            channel=channel_id,
            file=output_file,
            filename=attachment_filename,
            initial_comment=f"✅ <@{body['user']['id']}> - Converted *{original_filename}* ({plugin['input']} → {plugin['output']})"
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(output_file):
            os.remove(output_file)
        
        del pending_conversions[conversion_id]
        
        client.chat_postEphemeral(
            channel=channel_id,
            user=body["user"]["id"],
            text="✅ Conversion complete!"
        )
        
    except Exception as e:
        print(f"Error during conversion: {e}")
        client.chat_postEphemeral(
            channel=channel_id,
            user=body["user"]["id"],
            text=f"❌ Error during conversion: {str(e)}"
        )
        if os.path.exists(file_path):
            os.remove(file_path)
        if conversion_id in pending_conversions:
            del pending_conversions[conversion_id]


@app.command("/conversions")
def handle_conversions_command(ack, command, client):
    ack()
    
    if not plugins:
        client.chat_postEphemeral(
            channel=command["channel_id"],
            user=command["user_id"],
            text="❌ No conversion plugins available."
        )
        return
    
    conversions_dict = {}
    for plugin in plugins:
        input_fmt = plugin["input"].upper()
        output_fmt = plugin["output"].upper()
        if input_fmt not in conversions_dict:
            conversions_dict[input_fmt] = []
        conversions_dict[input_fmt].append(output_fmt)
    
    text_lines = ["*Available Conversions*\n"]
    for input_fmt in sorted(conversions_dict.keys()):
        outputs = ", ".join(sorted(conversions_dict[input_fmt]))
        text_lines.append(f"• *{input_fmt}* → {outputs}")
    
    text_lines.append(f"\n_Total: {len(plugins)} conversion(s) available_")
    
    client.chat_postEphemeral(
        channel=command["channel_id"],
        user=command["user_id"],
        text="\n".join(text_lines)
    )


if __name__ == "__main__":
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
   
    
    print("Starting Slack bot in Socket Mode...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()