import { useState } from "react";
const MovieSearch = () => {
  const [title, setTitle] = useState("");
  return (
    <div>
      <label>
        <p>Add liked movies: </p>
        <input type="text" value={title} onChange={() => setTitle} />
        <button>Add</button>
      </label>
    </div>
  );
};

export default MovieSearch;
