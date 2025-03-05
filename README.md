graph TD
    A[用户提问] --> B(Agent解析)
    B --> C{需要实时数据?}
    C -->|是| D[调用MQTT接口]
    C -->|否| E{需要历史数据?}
    E -->|是| F[查询MongoDB]
    E -->|否| G{需要外部数据?}
    G -->|是| H[调用天气/价格API]
    G -->|否| I[检索知识库]
    D --> J[综合所有数据]
    F --> J
    H --> J
    I --> J
    J --> K[生成最终回答]
    K --> L[返回用户]


langchain  agents

"zero-shot-react-description"：零样本（zero-shot）Agent，根据工具的描述动态选择工具。
"react-docstore"：用于文档检索的 Agent。
"self-ask-with-search"：支持自我提问和搜索的 Agent。
"conversational-react-description"：支持多轮对话的 Agent。

RetrievalQA 是 LangChain 中的一个工具链（Chain），用于实现基于检索的问答（Retrieval-Augmented Question Answering）。
它的核心功能是结合检索器（Retriever）和语言模型（LLM），通过 RetrievalQA，实现基于外部知识库的智能问答系统，
结合检索器和语言模型的优势，生成更准确和可靠的答案