import template from './vuex/template';
import assessmentItem from './vuex/assessmentItem';
import clipboard from './vuex/clipboard';
import contentNode from './vuex/contentNode';
import currentChannel from './vuex/currentChannel';
import importFromChannels from './vuex/importFromChannels';
import task from './vuex/task';
import * as actions from './actions';
import * as getters from './getters';
import * as mutations from './mutations';
import storeFactory from 'shared/vuex/baseStore';
import persistFactory from 'shared/vuex/persistFactory';
import DraggablePlugin from 'shared/vuex/draggablePlugin';

const store = storeFactory({
  state() {
    return {
      /**
       * The current view mode of the channel edit page,
       * which right now only controls the density of the
       * node list.
       *
       * See viewMode.* constants for options.
       */
      viewMode: null,

      /**
       * The view mode can be overridden by modals or panels,
       * and this allows for that to happen. See the
       * `isCompactViewMode` getter for how these are merged
       * to override the current `viewMode`.
       */
      viewModeOverrides: [],
    };
  },
  actions,
  mutations,
  getters,
  plugins: [DraggablePlugin, persistFactory('channelEdit', ['SET_VIEW_MODE'])],
  modules: {
    task,
    template,
    assessmentItem,
    clipboard,
    contentNode,
    currentChannel,
    importFromChannels,
  },
});

export default store;
