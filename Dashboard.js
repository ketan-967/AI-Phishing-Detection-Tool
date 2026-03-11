import React, { useState } from "react";
import { checkURL } from "../api";

export default function Dashboard() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState("");

  const handleCheck = async () => {
    const res = await checkURL(url);
    setResult(res.prediction);
  };

  return (
    <div>
      <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="Enter URL" />
      <button onClick={handleCheck}>Check</button>
      <h3>Result: {result}</h3>
    </div>
  );
}
