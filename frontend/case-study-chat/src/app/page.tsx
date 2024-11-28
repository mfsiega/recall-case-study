"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";

type Message = {
  role: string;
  content: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [paneText, setPaneText] = useState("This is the right side pane");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    try {
      const response = await fetch("http://localhost:8000/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Access-Control-Allow-Origin": "*",
        },
        body: JSON.stringify(userMessage),
      });
      const data = await response.json();
      console.log(data);
      const botMessage = { role: "assistant", content: data.reply };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const handleLinkClick = async (url: string) => {
    // Function that gets called when a link is clicked
    const response = await fetch(`http://localhost:8000${url}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    });
    const data = await response.json();
    console.log(data);
    setPaneText(data["summary"]);
  };

  return (
    <div className="flex h-screen">
      <div className="flex flex-col flex-1">
        <header className="p-4 bg-blue-600 text-white text-center">
          <h1 className="text-lg">AI Chatbot</h1>
        </header>

        <main className="flex-1 overflow-y-auto p-4 bg-gray-100">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`my-2 p-2 rounded-md ${
                message.role === "user"
                  ? "bg-blue-500 text-white self-end"
                  : "bg-gray-300 text-black self-start"
              }`}
            >
              <ReactMarkdown
                components={{
                  a: ({ node, ...props }) => (
                    <a
                      {...props}
                      href={props.href}
                      onClick={(e) => {
                        e.preventDefault(); // Prevent default link behavior
                        if (props.href) {
                          handleLinkClick(props.href); // Call custom function
                        }
                      }}
                      className="text-blue-600 underline cursor-pointer"
                    >
                      {props.children}
                    </a>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          ))}
        </main>

        <footer className="p-4 bg-white border-t">
          <div className="flex">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 p-2 border rounded-l-md"
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button
              onClick={sendMessage}
              className="p-2 bg-blue-600 text-white rounded-r-md"
            >
              Send
            </button>
          </div>
        </footer>
      </div>

      <aside className="w-64 bg-white p-4 border-l border-gray-300 overflow-y-auto">
        <h2 className="text-lg font-semibold">Summary</h2>
        <p>
          <ReactMarkdown>{paneText}</ReactMarkdown>
        </p>
      </aside>
    </div>
  );
}
