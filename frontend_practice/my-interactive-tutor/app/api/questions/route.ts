import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    const questionsDir = path.join(process.cwd(), "public", "questions");
    const files = fs.readdirSync(questionsDir);

    // For each file, extract the tag from first part of the filename
    // e.g., "1_basic.png" => tag = "1"
    const questions = files.map((file) => {
      const [tag] = file.split("_");
      return { tag, filename: file };
    });

    return NextResponse.json(questions);
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 500 });
  }
}
