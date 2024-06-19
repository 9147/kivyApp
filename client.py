# import asyncio
# import websockets
# import json

# def get_stored_token():
#     try:
#         with open('token.json', 'r') as f:
#             data = json.load(f)
#             return data.get('token')
#     except FileNotFoundError:
#         return ""
    
# async def connect_to_server():
#   uri = "ws://127.0.0.1:8000/updates/register/?token="+get_stored_token()  # Replace with your actual URL
#   async with websockets.connect(uri) as websocket:
#     # Print received messages from the server (optional)
#     async for message in websocket:
#       print(message)

#     # Send a message to the server (optional)
#     await websocket.send("Hello from the client!")

# # Run the coroutine
# asyncio.run(connect_to_server())