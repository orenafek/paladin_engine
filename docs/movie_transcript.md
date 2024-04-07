# Demo

## Script

1. In this demo, we will demonstrate the use of PaLaDiN - Time Travel Debugger with Semantic Queries to debug an
   example program.
2. In this program, A Server has a list of jobs that are run by different types of workers.
3. A Job object has a unique id and a type that is either a text, an image, an audio or a video.
4. A Server object has two lists, "todo": for jobs that need to be consumed, and "summaries": for jobs that have been
   operated by workers.
5. There are four kinds of workers, all inherit Worker class.
6. TimelessWorker: operates on images and texts.
7. PlayableWorker: operates on audios and videos.
8. VisualWorker: operates on images and videos.
9. AllTypesWorker: operates on all four types.
10. In its "consume" method, a worker object pops a job from the server's "todo" list into its "ongoing" field and calls
    its "operate" function.
11. In its "operate" function, each worker should push a summary for that job, if its able to operate on it, or push it
    back to the todo list otherwise.
12. In the main program, 20 jobs are created and shuffled.
13. As long as there are jobs todo, a random worker is picked to consume a job.
14. In the end, the server verifies that there are as many summaries as there were jobs at the beginning.

15. The program has raised an exception, the len of the jobs and server.summaries mismatch. lets use PaLaDiN to debug
    it.

16. The lists' sizes differ, so we understand that there is a job missing, let's find out which one.
17. The job object is too verbose, let's write a customizer code to focus by shortening its display: id + the first
    letter of its type.
18. The missing job is '14A' (14 Audio).
19. By observing the code, we can see that normally a job goes through the process of:
    jobs -> server.todo -> <Some worker>.ongonig -> <In Worker::operate>> -> server.summaries
20. Let's ask PaLaDiN when this invariant is broken by looking for an object that has left jobs but is nowhere in each
    of the other fields by looking at "the difference".
21. We can see that each job leaves "jobs" and is nowhere to be found, until it is in "the difference", once, at the
    time between the call to server.todo.pop() and before the assignment to ongoing.
22. Job "14A", though once sticks on "the difference", never leaves it.
23. Let's focus on the first time "14A" has appeared on the difference, before it got stuck in there.
24. We understand that a worker have had "14A" in its ongoing field, but never pushed it to summaries. 
25. Probably there is a bug in its operate function.
26. Let's find which worker was that.
27. We can see that VisualWorker has forgotten to include "Audio" in its case that pushes back the job to "todo".
28. We've found the bug!