export interface Email {
    id: number;
    sender: string;
    subject: string;
    body: string;
    snippet: string;
    received_at: string;
    is_read: boolean;
    labels: string;
    has_reply: boolean;
    reply_content: string;
}
