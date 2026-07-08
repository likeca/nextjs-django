"use client";

import { Button } from "@/components/ui/button";
import { clientRequest } from "@/lib/api/browser";
import { useState } from "react";

export function GroupsButton() {
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleClick = async () => {
    setLoading(true);
    try {
      const data = await clientRequest("/api/groups/");
      setResult(JSON.stringify(data, null, 2));
    } catch (e) {
      setResult(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <Button size="lg" onClick={handleClick} disabled={loading}>
        {loading ? "Loading..." : "Groups"}
      </Button>
      {result && (
        <pre className="text-left p-4 rounded text-sm overflow-auto">
          {result}
        </pre>
      )}
    </div>
  );
}
