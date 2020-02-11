import translator from './translator';

import { AssessmentItemTypes } from 'frontend/channelEdit/constants';

/**
 * Get correct answer index/indices out of an array of answer objects.
 * @param {String} questionType single/multiple selection, true/false, input question
 * @param {Array} answers An array of answer objects { answer: ..., correct: ..., ...}
 * @returns {Number|null|Array} Returns a correct answer index or null for single selection
 * or true/false question. Returns an array of correct answers indices for multiple selection
 * or input question.
 */
export const getCorrectAnswersIndices = (questionType, answers) => {
  if (!questionType || !answers || !answers.length) {
    return null;
  }

  if (
    questionType === AssessmentItemTypes.SINGLE_SELECTION ||
    questionType === AssessmentItemTypes.TRUE_FALSE
  ) {
    const idx = answers.findIndex(answer => answer.correct);
    return idx === -1 ? null : idx;
  }

  return answers
    .map((answer, idx) => {
      return answer.correct ? idx : undefined;
    })
    .filter(idx => idx !== undefined);
};

/**
 * Updates `correct` fields of answers based on index/indexes stored in `correctAnswersIndices`.
 * @param {Array} answers An array of answer objects { answer: ..., correct: ..., ...}
 * @param {Number|null|Array} correctAnswersIndices A correct answer index or an array
 * of correct answers indexes.
 * @returns {Array} An array of answer objects with updated `correct` fields.
 */
export const mapCorrectAnswers = (answers, correctAnswersIndices) => {
  if (!answers || !answers.length) {
    return null;
  }

  return answers.map((answer, idx) => {
    const isAnswerCorrect =
      correctAnswersIndices === idx ||
      (Array.isArray(correctAnswersIndices) && correctAnswersIndices.includes(idx));

    return {
      ...answer,
      correct: isAnswerCorrect,
    };
  });
};

/**
 * Update answers to correspond to a question type:
 * - multiple selection: No answers updates needed.
 * - input question: Make all answers correct.
 * - true/false: Remove answers in favour of new true/false values.
 * - single selection: Keep first correct choice only if there is any.
 *                     Otherwise mark first choice as correct.
 * @param {String} newQuestionType single/multiple selection, true/false, input question
 * @param {Array} answers An array of answer objects.
 * @returns {Array} An array of updated answer objects.
 */
export const updateAnswersToQuestionType = (questionType, answers) => {
  const NEW_TRUE_FALSE_ANSWERS = [
    { answer: translator.translate('true'), correct: true, order: 1 },
    { answer: translator.translate('false'), correct: false, order: 2 },
  ];

  if (!answers || !answers.length) {
    if (questionType === AssessmentItemTypes.TRUE_FALSE) {
      return NEW_TRUE_FALSE_ANSWERS;
    } else {
      return [];
    }
  }

  let answersCopy = JSON.parse(JSON.stringify(answers));

  switch (questionType) {
    case AssessmentItemTypes.MULTIPLE_SELECTION:
      return answersCopy;

    case AssessmentItemTypes.INPUT_QUESTION:
      return answersCopy.map(answer => {
        answer.correct = true;
        return answer;
      });

    case AssessmentItemTypes.TRUE_FALSE:
      return NEW_TRUE_FALSE_ANSWERS;

    case AssessmentItemTypes.SINGLE_SELECTION: {
      let firstCorrectAnswerIdx = answers.findIndex(answer => answer.correct === true);
      if (firstCorrectAnswerIdx === -1) {
        firstCorrectAnswerIdx = 0;
      }

      const newAnswers = answersCopy.map(answer => {
        answer.correct = false;
        return answer;
      });

      newAnswers[firstCorrectAnswerIdx].correct = true;

      return newAnswers;
    }
  }
};

/**
 * Convert a node retrieved from API to a format suitable for any
 * further client-side work:
 * - if node has some assessment items, parse stringified data
 * - make sure that everything is properly sorted by order
 */
export const parseNode = node => {
  if (node.assessment_items && node.assessment_items.length) {
    node.assessment_items = node.assessment_items.map(item => {
      let answers;
      let hints;

      // data can come from API that returns answers and hints as string
      if (typeof item.answers === 'string') {
        answers = JSON.parse(item.answers);
      } else {
        answers = item.answers ? item.answers : [];
      }

      if (typeof item.hints === 'string') {
        hints = JSON.parse(item.hints);
      } else {
        hints = item.hints ? item.hints : [];
      }

      answers.sort((answer1, answer2) => (answer1.order > answer2.order ? 1 : -1));
      hints.sort((hint1, hint2) => (hint1.order > hint2.order ? 1 : -1));

      return {
        ...item,
        answers,
        hints,
      };
    });

    node.assessment_items.sort((item1, item2) => (item1.order > item2.order ? 1 : -1));
  }

  return node;
};

// TODO @MisRob: Utilities below are not specific to exercise creation.
// Find/create a file higher in the project structure for general stuff.
/**
 * Insert an item into an array before another item.
 * @param {Array} arr
 * @param {Number} idx An index of an item before which
 *                     a new item will be inserted.
 * @param {*} item A new item to be inserted into an array.
 */
export const insertBefore = (arr, idx, item) => {
  const newArr = JSON.parse(JSON.stringify(arr));
  const insertAt = Math.max(0, idx);
  newArr.splice(insertAt, 0, item);

  return newArr;
};

/**
 * Insert an item into an array after another item.
 * @param {Array} arr
 * @param {Number} idx An index of an item after which
 *                     a new item will be inserted.
 * @param {*} item A new item to be inserted into an array.
 */
export const insertAfter = (arr, idx, item) => {
  const newArr = JSON.parse(JSON.stringify(arr));
  const insertAt = Math.min(arr.length, idx + 1);
  newArr.splice(insertAt, 0, item);

  return newArr;
};

/**
 * Swap two elements of an array
 * @param {Array} arr
 * @param {Number} idx1
 * @param {Number} idx2
 */
export const swapElements = (arr, idx1, idx2) => {
  const newArr = JSON.parse(JSON.stringify(arr));
  [newArr[idx1], newArr[idx2]] = [newArr[idx2], newArr[idx1]];

  return newArr;
};