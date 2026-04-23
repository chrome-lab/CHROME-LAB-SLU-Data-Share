// Auto-generated. Do not edit!

// (in-package quori_gui.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class Opcmd {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.data = null;
      this.angle_dist = null;
    }
    else {
      if (initObj.hasOwnProperty('data')) {
        this.data = initObj.data
      }
      else {
        this.data = '';
      }
      if (initObj.hasOwnProperty('angle_dist')) {
        this.angle_dist = initObj.angle_dist
      }
      else {
        this.angle_dist = 0.0;
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type Opcmd
    // Serialize message field [data]
    bufferOffset = _serializer.string(obj.data, buffer, bufferOffset);
    // Serialize message field [angle_dist]
    bufferOffset = _serializer.float64(obj.angle_dist, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type Opcmd
    let len;
    let data = new Opcmd(null);
    // Deserialize message field [data]
    data.data = _deserializer.string(buffer, bufferOffset);
    // Deserialize message field [angle_dist]
    data.angle_dist = _deserializer.float64(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    let length = 0;
    length += _getByteLength(object.data);
    return length + 12;
  }

  static datatype() {
    // Returns string type for a message object
    return 'quori_gui/Opcmd';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '8e95fd03b16cd7241921e03a50a02cad';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    string data
    float64 angle_dist
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new Opcmd(null);
    if (msg.data !== undefined) {
      resolved.data = msg.data;
    }
    else {
      resolved.data = ''
    }

    if (msg.angle_dist !== undefined) {
      resolved.angle_dist = msg.angle_dist;
    }
    else {
      resolved.angle_dist = 0.0
    }

    return resolved;
    }
};

module.exports = Opcmd;
