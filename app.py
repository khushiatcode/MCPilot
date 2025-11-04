import asyncio
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_use import MCPAgent, MCPClient
import gradio as gr

# Global agent and client instances
agent = None
client = None

async def initialize_agent():
    """Initialize the MCP agent and client."""
    global agent, client
    
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")

    config_file = "browser_mcp.json"
    
    # create MCP client and agent with memory enabled
    print("Creating MCP client...")
    client = MCPClient.from_config_file(config_file)
    
    # Wait longer for servers to initialize and establish connections
    print("Waiting for MCP servers to initialize...")
    for i in range(5):  # Wait up to 5 seconds in 1-second increments
        await asyncio.sleep(1)
        if hasattr(client, 'sessions') and client.sessions:
            print(f"MCP sessions established: {list(client.sessions.keys())}")
            break
        print(f"Waiting for sessions... ({i+1}/5)")
    
    # Final check if sessions are established
    if hasattr(client, 'sessions'):
        session_count = len(client.sessions) if client.sessions else 0
        print(f"MCP sessions: {session_count} session(s)")
        if session_count == 0:
            print("Warning: No MCP sessions found after initialization")
    else:
        print("Warning: Client has no 'sessions' attribute")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api_key)

    # create agent with memory enabled
    print("Creating MCP agent...")
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=15,
        memory_enabled=True,
    )
    
    print("Agent initialized successfully")
    return agent, client

async def chat_with_agent(message):
    """Handle chat messages in the Gradio interface."""
    global agent, client
    
    if not agent:
        return "Error: Agent not initialized. Please refresh the page."
    
    # Handle special commands first (before checking sessions)
    if message.lower().strip() == "clear":
        agent.clear_conversation_history()
        return "Conversation history cleared."
    
    if message.lower().strip() == "servers":
        if client and hasattr(client, 'sessions') and client.sessions:
            servers_list = "\n".join([f"✓ {name}" for name in client.sessions.keys()])
            return f"Connected MCP Servers:\n{servers_list}"
        else:
            return "No MCP servers connected. Sessions may have closed."
    
    # Check sessions - but don't fail if they're empty, just try to use the agent
    # The agent might handle reconnection internally
    session_status = "unknown"
    if client and hasattr(client, 'sessions'):
        session_status = "empty" if not client.sessions else f"active ({len(client.sessions)} sessions)"
    print(f"Session status before chat: {session_status}")
    
    try:
        # Run the agent with user input
        # The agent should handle connection issues internally
        print(f"Processing message: {message[:50]}...")
        response = await agent.run(message)
        print("Response received successfully")
        return response
    except Exception as e:
        error_msg = str(e)
        print(f"Error in chat_with_agent: {error_msg}")
        import traceback
        traceback.print_exc()
        
        # Try to reconnect if connection was closed
        if "Connection closed" in error_msg or "closed" in error_msg.lower():
            print("Attempting to reinitialize agent...")
            try:
                await initialize_agent()
                # Try once more after reconnection
                try:
                    response = await agent.run(message)
                    return response
                except Exception as retry_e:
                    return f"Error after reconnection attempt: {str(retry_e)}\n\nPlease refresh the page to fully reconnect."
            except Exception as reconnect_e:
                return f"Error: MCP connection closed and reconnection failed.\n\nError: {str(reconnect_e)}\n\nPlease refresh the page or check the terminal for details."
        
        return f"Error: {error_msg}"

def get_connected_servers():
    """Get list of connected MCP servers."""
    global client
    if client and hasattr(client, 'sessions') and client.sessions:
        return ", ".join(client.sessions.keys())
    return "None"

def create_ui():
    """Create and launch the Gradio UI."""
    # Create Gradio interface - initialize agent lazily
    with gr.Blocks(title="MCPilot", theme=gr.themes.Soft()) as demo:
        status_text = gr.Markdown(
            """
            # 🚀 MCPilot
            
            An intelligent assistant powered by **Google Gemini** with access to multiple tools:
            - 🌐 **Browser Automation** (Playwright)
            - 🔍 **Web Search** (DuckDuckGo)
            - 📁 **File Operations** (Filesystem)
            - 🔧 **Git Operations** (Git)
            
            **Status:** Initializing agent...
            
            ---
            """
        )
        
        chatbot = gr.Chatbot(
            label="Chat",
            height=500,
            show_copy_button=True,
            avatar_images=(None, "🤖")
        )
        
        with gr.Row():
            msg = gr.Textbox(
                label="Your Message",
                placeholder="Type your message here... (Type 'clear' to reset conversation, 'servers' to see connected servers)",
                scale=3,
                container=False
            )
            submit_btn = gr.Button("Send", variant="primary", scale=1)
            reconnect_btn = gr.Button("🔄 Reconnect", variant="secondary", scale=1)
        
        gr.Examples(
            examples=[
                "Search the web for the latest Python news",
                "List files in the current directory",
                "Check git status",
                "What can you do?",
            ],
            inputs=msg
        )
        
        def user(user_message, history):
            return "", history + [[user_message, None]]
        
        async def bot(history):
            global agent
            if not agent:
                # Try to initialize if not already done
                try:
                    await initialize_agent()
                except Exception as e:
                    history[-1][1] = f"Error initializing agent: {str(e)}. Please refresh the page."
                    return history
            
            user_message = history[-1][0]
            try:
                response = await chat_with_agent(user_message)
                history[-1][1] = response
            except Exception as e:
                error_msg = str(e)
                print(f"Error in bot function: {error_msg}")
                import traceback
                traceback.print_exc()
                history[-1][1] = f"Error: {error_msg}"
            return history
        
        # Don't initialize on load - let it initialize on first message
        # This prevents blocking the UI
        
        async def reconnect():
            """Reconnect to MCP servers."""
            global agent, client
            try:
                # Close existing sessions if any
                if client and hasattr(client, 'sessions') and client.sessions:
                    await client.close_all_sessions()
                
                # Reinitialize
                await initialize_agent()
                servers = get_connected_servers()
                return f"""
                # 🚀 MCPilot
                
                An intelligent assistant powered by **Google Gemini** with access to multiple tools:
                - 🌐 **Browser Automation** (Playwright)
                - 🔍 **Web Search** (DuckDuckGo)
                - 📁 **File Operations** (Filesystem)
                - 🔧 **Git Operations** (Git)
                
                **Status:** ✓ Reconnected ({servers})
                
                ---
                """
            except Exception as e:
                return f"""
                    # 🚀 MCPilot
                    
                    **Status:** ✗ Reconnection failed: {str(e)}
                    
                    ---
                    """
        
        # Initialize agent in a separate thread when UI is ready
        def update_status():
            """Update status text with current connection info."""
            servers = get_connected_servers()
            if agent:
                status = "✓ Ready"
            else:
                status = "⏳ Not initialized (will connect on first message)"
            
            return f"""
            # 🚀 MCPilot
            
            An intelligent assistant powered by **Google Gemini** with access to multiple tools:
            - 🌐 **Browser Automation** (Playwright)
            - 🔍 **Web Search** (DuckDuckGo)
            - 📁 **File Operations** (Filesystem)
            - 🔧 **Git Operations** (Git)
            
            **Status:** {status} ({servers})
            
            ---
            """
        
        # Update status on load
        demo.load(update_status, outputs=status_text)
        reconnect_btn.click(reconnect, outputs=status_text)
        
        msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        )
        submit_btn.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot, chatbot, chatbot
        )
        
        gr.Markdown(
            """
            ---
            ### 💡 Tips:
            - Type **'clear'** to reset conversation history
            - Type **'servers'** to see connected MCP servers
            - The assistant has memory and remembers our conversation
            - Ask it to browse websites, search the web, manage files, or use git!
            """
        )
    
    return demo

if __name__ == "__main__":
    try:
        demo = create_ui()
        print("\n🚀 Starting Gradio server...")
        print("📱 Access the UI at: http://localhost:7860")
        demo.launch(share=False, server_name="0.0.0.0", server_port=7860, show_error=True)
    except Exception as e:
        print(f"✗ Error launching UI: {e}")
        import traceback
        traceback.print_exc()
        