import { useState } from "react";
const MovieSearch = () => {
  const [title, setTitle] = useState("");
  return (
    <div>
      <input type="text" value={title} onChange={() => setTitle} />
    </div>
  );
};

export default MovieSearch;
