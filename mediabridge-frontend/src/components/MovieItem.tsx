import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Movie } from "@/types/Movie";

const MovieItem = ({ movie }: { movie: Movie }) => {
  return (
    <Card className="max-w-[12vw] flex flex-col items-center">
      <CardHeader>
        <CardTitle>{movie.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <img src={movie.image} alt={movie.title} />
      </CardContent>
      <CardFooter>{movie.year}</CardFooter>
    </Card>
  );
};

export default MovieItem;
