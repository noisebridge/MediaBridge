import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Movie } from "../types/Movie"; // adjust path if needed

type Props = {
  setMovies: React.Dispatch<React.SetStateAction<Movie[]>>;
};

const MovieSearch = ({ setMovies }: Props) => {
  const [title, setTitle] = useState("");

  const handleAddMovie = () => {
    if (!title.trim()) return;

    setMovies((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        title,
        year: new Date().getFullYear(),
        image: "https://via.placeholder.com/150",
      },
    ]);

    setTitle(""); 
  };

  return (
    <Card className="w-full max-w-md flex flex-col items-center mb-4">
      <CardHeader>
        <CardTitle>Mediabridge</CardTitle>
        <CardDescription>Add liked movies</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex w-full items-center space-x-2">
          <Input
            type="text"
            placeholder="The Room"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <Button onClick={handleAddMovie}>Add Movie</Button>
        </div>
      </CardContent>
      <CardFooter>
        <Button type="submit">Get Recommendations</Button>
      </CardFooter>
    </Card>
  );
};

export default MovieSearch;