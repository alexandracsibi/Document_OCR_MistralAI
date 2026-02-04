import { apiFetch } from "./client";

export type OcrUploadArgs = {
  uri: string;

  uid: string;
  docType: string; // e.g. "ID_BACK"

  // Optional overrides
  path?: string; // default: "/v1/process"
  filename?: string; // default: "capture.jpg"
  mimeType?: string; // default: "image/jpeg"
};

export async function uploadToOcrService(args: OcrUploadArgs): Promise<any> {
  const {
    uri,
    uid,
    docType,
    path = "/v1/process",
    filename = "capture.jpg",
    mimeType = "image/jpeg",
  } = args;

  if (!uid.trim()) throw new Error("uid is required");
  if (!docType.trim()) throw new Error("doc_type is required");

  const form = new FormData();

  // IMPORTANT: names must match your OCR service contract exactly
  form.append("uid", uid);
  form.append("doc_type", docType);

  // File field name must be "file"
  form.append("file", { uri, name: filename, type: mimeType } as any);

  const res = await apiFetch(path, {
    method: "POST",
    body: form,
    // Do NOT set Content-Type manually; RN will set boundary.
  });

  const text = await res.text().catch(() => "");
  if (!res.ok) {
    throw new Error(`OCR request failed (${res.status}): ${text}`);
  }

  // Parse JSON if possible
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}
