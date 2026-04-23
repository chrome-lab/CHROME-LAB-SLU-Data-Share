// Auto-generated. Do not edit!

// (in-package quori_interactions.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class ArmsCmd {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.r_shoulder_pitch = null;
      this.r_shoulder_roll = null;
      this.l_shoulder_pitch = null;
      this.l_shoulder_roll = null;
      this.waist_pitch = null;
    }
    else {
      if (initObj.hasOwnProperty('r_shoulder_pitch')) {
        this.r_shoulder_pitch = initObj.r_shoulder_pitch
      }
      else {
        this.r_shoulder_pitch = 0.0;
      }
      if (initObj.hasOwnProperty('r_shoulder_roll')) {
        this.r_shoulder_roll = initObj.r_shoulder_roll
      }
      else {
        this.r_shoulder_roll = 0.0;
      }
      if (initObj.hasOwnProperty('l_shoulder_pitch')) {
        this.l_shoulder_pitch = initObj.l_shoulder_pitch
      }
      else {
        this.l_shoulder_pitch = 0.0;
      }
      if (initObj.hasOwnProperty('l_shoulder_roll')) {
        this.l_shoulder_roll = initObj.l_shoulder_roll
      }
      else {
        this.l_shoulder_roll = 0.0;
      }
      if (initObj.hasOwnProperty('waist_pitch')) {
        this.waist_pitch = initObj.waist_pitch
      }
      else {
        this.waist_pitch = 0.0;
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type ArmsCmd
    // Serialize message field [r_shoulder_pitch]
    bufferOffset = _serializer.float32(obj.r_shoulder_pitch, buffer, bufferOffset);
    // Serialize message field [r_shoulder_roll]
    bufferOffset = _serializer.float32(obj.r_shoulder_roll, buffer, bufferOffset);
    // Serialize message field [l_shoulder_pitch]
    bufferOffset = _serializer.float32(obj.l_shoulder_pitch, buffer, bufferOffset);
    // Serialize message field [l_shoulder_roll]
    bufferOffset = _serializer.float32(obj.l_shoulder_roll, buffer, bufferOffset);
    // Serialize message field [waist_pitch]
    bufferOffset = _serializer.float32(obj.waist_pitch, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type ArmsCmd
    let len;
    let data = new ArmsCmd(null);
    // Deserialize message field [r_shoulder_pitch]
    data.r_shoulder_pitch = _deserializer.float32(buffer, bufferOffset);
    // Deserialize message field [r_shoulder_roll]
    data.r_shoulder_roll = _deserializer.float32(buffer, bufferOffset);
    // Deserialize message field [l_shoulder_pitch]
    data.l_shoulder_pitch = _deserializer.float32(buffer, bufferOffset);
    // Deserialize message field [l_shoulder_roll]
    data.l_shoulder_roll = _deserializer.float32(buffer, bufferOffset);
    // Deserialize message field [waist_pitch]
    data.waist_pitch = _deserializer.float32(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    return 20;
  }

  static datatype() {
    // Returns string type for a message object
    return 'quori_interactions/ArmsCmd';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return '18963acf222a3961918de358f517947a';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    float32 r_shoulder_pitch
    float32 r_shoulder_roll
    float32 l_shoulder_pitch
    float32 l_shoulder_roll
    float32 waist_pitch
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new ArmsCmd(null);
    if (msg.r_shoulder_pitch !== undefined) {
      resolved.r_shoulder_pitch = msg.r_shoulder_pitch;
    }
    else {
      resolved.r_shoulder_pitch = 0.0
    }

    if (msg.r_shoulder_roll !== undefined) {
      resolved.r_shoulder_roll = msg.r_shoulder_roll;
    }
    else {
      resolved.r_shoulder_roll = 0.0
    }

    if (msg.l_shoulder_pitch !== undefined) {
      resolved.l_shoulder_pitch = msg.l_shoulder_pitch;
    }
    else {
      resolved.l_shoulder_pitch = 0.0
    }

    if (msg.l_shoulder_roll !== undefined) {
      resolved.l_shoulder_roll = msg.l_shoulder_roll;
    }
    else {
      resolved.l_shoulder_roll = 0.0
    }

    if (msg.waist_pitch !== undefined) {
      resolved.waist_pitch = msg.waist_pitch;
    }
    else {
      resolved.waist_pitch = 0.0
    }

    return resolved;
    }
};

module.exports = ArmsCmd;
