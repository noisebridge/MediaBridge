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

const MovieSearch = () => {
  const [title, setTitle] = useState("");
  return (
    <Card className="flex flex-col items-center">
      <CardHeader>
        <CardTitle>Mediabridge</CardTitle>
        <CardDescription>Add liked movies</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex w-full max-w-sm items-center space-x-2">
          <Input
            type="text"
            placeholder="The Room"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <Button>Add Movie</Button>
        </div>
      </CardContent>
      <CardFooter>
        <Button type="submit">Get Recommendations</Button>
      </CardFooter>
    </Card>
  );
};

export default MovieSearch;
