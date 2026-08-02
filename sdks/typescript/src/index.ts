/**
 * Official TypeScript SDK for AI Growth Operating System (AGOS).
 */

export class AGOSClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(config: { apiKey: string; baseUrl?: string }) {
    this.apiKey = config.apiKey;
    this.baseUrl = (config.baseUrl || 'http://localhost:8000/api').replace(/\/$/, '');
  }

  async health(): Promise<{ status: string }> {
    const res = await fetch(`${this.baseUrl}/health`);
    return res.json();
  }

  async listProjects(): Promise<any[]> {
    const res = await fetch(`${this.baseUrl}/v1/projects`, {
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    const data = await res.json();
    return data.items || [];
  }
}
