class SchedPredicate<code pred> {
  code Predicate = pred;
}
def NoSchedPred : SchedPredicate<[{true}]>;
